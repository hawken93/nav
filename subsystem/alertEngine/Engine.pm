#! /usr/bin/env perl
#
# Engine.pm
#
#    This is the main class, running continually, retrieving data and
# sending alerts.
#
# Copyright 2002, 2003 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV)
#
# NAV is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# NAV is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NAV; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# Authors: Andreas Aakre Solberg, UNINETT
#          Arne �sleb�, UNINETT
#

package NAV::AlertEngine::Engine;

#use lib '/home/arneos/perl/lib/perl5/site_perl/5.8.0/i386-linux-thread-multi';

use warnings;
use strict 'vars';
use diagnostics;
use DBI;
use NAV::AlertEngine::UserGroups;
use NAV::AlertEngine::Alert;
use NAV::AlertEngine::QueuedAlerts;
use NAV::AlertEngine::EquipmentGroups;
use NAV::AlertEngine::NewAlerts;
use NAV::AlertEngine::User;
use NAV::AlertEngine::Log;

# Konstruktor..
sub new {
	my ($class,$cfg)=@_;
	my $this = {};
	# oppretter en databaseforbindelse til profildatabasen
	                              # db host name passwd
	$this->{dbh_user} = DBI->connect("dbi:Pg:dbname=$cfg->{usersdb_name};host='$cfg->{usersdb_host}'",$cfg->{usersdb_loginname}, $cfg->{usersdb_passwd}, undef) || die $DBI::errstr;
	$this->{dbh_alert} = DBI->connect("dbi:Pg:dbname='$cfg->{alertdb_name}';host='$cfg->{alertdb_host}'", $cfg->{alertdb_loginname}, $cfg->{alertdb_passwd}, undef) || die $DBI::errstr;

	$this->{cfg}=$cfg;
	$this->{log}=NAV::AlertEngine::Log->new();

	bless $this,$class;                                          

	return $this;
}

# Sletter PID-filen.
sub delete_pidfile() {
    my $pidfile=shift;
    if (-f $pidfile) {
	unlink($pidfile);
    }
}

# funksjon som kalles n�r daemonen kj�res ned..
sub shutdownConstruct() {
	my $this = shift;

	# returnerer en lukning (closure) som inneholder referanse til riktig Engine::objekt.
	return sub {
		my $signal_recv = shift;
		&delete_pidfile($this->{cfg}->{pidfile});
		$this->{log}->printlog("Engine","shutdownConstruct",$this->{log}->{informational}, "Got signal :" . $signal_recv . ":! nice shutdown.");
		
		$this->disconnectDB();

		exit(0);
	}
}

#Disconnects from DB
sub disconnectDB()
  {
    my $this=shift;
    $this->{dbh_user}->disconnect;
    $this->{dbh_alert}->disconnect;
  }

sub checkAlerts()
#Check new alerts
  {
    my $this=shift;

    my $nA=NAV::AlertEngine::NewAlerts->new($this->{dbh_alert},$this->{lastAlertID});
    my $num=$nA->getAlertNum();
    my $uG=undef;
    my $eG=undef;
    if(!defined $num) {
	$num=0;
    }

    $uG=NAV::AlertEngine::UserGroups->new($this->{dbh_user});
    $eG=NAV::AlertEngine::EquipmentGroups->new($this->{dbh_user});
  
    #Collect infor about queued alerts
    my $qa=NAV::AlertEngine::QueuedAlerts->new($this->{dbh_alert},$this->{dbh_user});

    #Get list of users
    my $users=$this->{dbh_user}->selectall_arrayref("select id from account a, preference p where a.id=p.accountid and p.activeprofile is not NULL") || $this->{log}->printlog("Engine","checkAlerts",$Log::error, "could not get list of active users");

   foreach my $userid (@$users)
      {
	my $user=NAV::AlertEngine::User->new($userid->[0],$this->{dbh_user},$this->{cfg});
	$user->checkAlertQueue($qa,$eG);
	if($num)
	  #If there are new active alarts
	  {
	    $user->checkNewAlerts($nA,$uG,$eG);
	  }
      }
	
    #Delete alerts
    if($num) {
	for(my $c=0;$c<$num;$c++) {
	    my $alert=$nA->getAlert($c);
	    $alert->delete();
	}
    }
    $this->{lastAlertID}=$nA->finished();
  }



# Dette er selve deamonen som g�r i evig l�kke til den blir stanset.
sub run() {
	my $this = shift;

	# shutdownconstruct returnerer en funksjonsreferanse til en funksjon
	# som har en referanse til $this objektet innebygget i sin scope.
	# Den er n�dt til � ha en referanse til $this for � kunne kalle close
	# p� databasehandleren som ligger lagret som en instansvaribel i objektet.
	$SIG{QUIT} = &shutdownConstruct($this);
	$SIG{TERM} = &shutdownConstruct($this);
	
	while (1) {
		my $tf = time();
		#print "Running and living happy...\n";
		
		$this->checkAlerts();

		my $te = time();
		my $tdiff = $te - $tf;
		#print "Elapsed time alertsession: " . $tdiff . " seconds.\n\n\n";
		
#		open var_dump, '>/tmp/vardump.txt';
#		print  var_dump Dumper($this);
#		close (var_dump);
		sleep($this->{cfg}->{sleep});
	}
}

1;
