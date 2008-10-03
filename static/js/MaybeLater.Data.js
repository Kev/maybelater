MaybeLater.Data = function() {
    var dataRecord = Ext.data.Record.create([
		{name: 'name', mapping: 'fields.name'},
		{name: 'description', mapping: 'fields.notes'},
		{name: 'effort', type: 'int', mapping: 'fields.effort'},
		{name: 'priority', type: 'int', mapping: 'fields.priority'},
		{name: 'startDate', type: 'date', dateFormat: 'n/j h:ia', mapping:'fields.startDate'},
		{name: 'dueDate', type: 'date', dateFormat: 'n/j h:ia', mapping:'fields.dueDate'}
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