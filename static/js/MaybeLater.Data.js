MaybeLater.Data = function() {
    var dataRecord = Ext.data.Record.create([
		{name: 'name'},
		{name: 'description'},
		{name: 'effort', type: 'int'},
		{name: 'priority', type: 'int'},
		{name: 'startDate', type: 'date', dateFormat: 'n/j h:ia'},
		{name: 'dueDate', type: 'date', dateFormat: 'n/j h:ia'}
	]);
    
    /*var data = [
		['Something','raaar',1],
		['Thingsome','',2],
		['Another Thing','Stuff',5]
	];
    
    var reader = new Ext.data.ArrayReader({}, dataRecord);*/
    
    var reader = new Ext.data.JsonReader({
        root: 'tasks', 
        totalProperty: 'total',
        //record: 'item' //the XML delimiter tag for each record (row of data)
        },                                             
        dataRecord
    );
    
    var dataStore;
    
    return {
        createStore: function() {
            dataStore = new Ext.data.Store({
                proxy: new Ext.data.HttpProxy({
                    url: '/v2/tasks', 
                    method: 'GET'
                }),
                sortInfo:{field: 'priority', direction: "DESC"},
        		//data: data,
        		reader: reader
        	});
        	dataStore.load();
        	return dataStore;
        }
    };
    
    
}();