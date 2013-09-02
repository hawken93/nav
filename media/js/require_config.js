var require = {
    baseUrl: '/js',
    waitSeconds: 7, // default
    paths: {
        "libs": "libs",
        "resources": "resources",
        "libs-amd": "resources/libs",
        "plugins": "src/plugins",
        "dt_plugins": "src/dt_plugins",
        "info": "src/info",
        "netmap": "src/netmap"
    },
    shim: {
        'libs/foundation.min': ['libs/jquery'],
        'libs/FixedColumns.min': ['libs/jquery'],
        'libs/jquery-ui-1.8.21.custom.min': ['libs/jquery'],
        'libs/jquery.dataTables.min': ['libs/jquery'],
        'libs/jquery.tablesorter.min': ['libs/jquery'],
        'libs/jquery.nivo.slider.pack': ['libs/jquery'],
        'libs/downloadify.min': ['libs/jquery', 'libs/swfobject'],
        'libs/spin.min': ['libs/jquery'],
        'libs/underscore': {
            exports: '_'
        },
        'libs/backbone': ["libs/underscore", "libs/jquery"],
        'libs/backbone-eventbroker': ['libs/backbone']

    }
};
