MaybeLater.TaskList = function() {
	var taskGrid;
	return {
        create: function(dataStore, region) {
			taskGrid = new Ext.grid.GridPanel({region: region,
			    columns: [
					{header: 'Name', width: 120, sortable: true, dataIndex: 'name'},
					{header: 'Priority', width: 90, sortable: true, dataIndex: 'priority'},
					{header: 'Effort', width: 90, sortable: true, dataIndex: 'effort'},
					{header: 'Start', width: 90, sortable: true, dataIndex: 'startDate'},
					{header: 'Due', width: 90, sortable: true, dataIndex: 'dueDate'},
				],
				store: dataStore,
				region: region,
				title: 'Tasks',
				frame: true,
				viewConfig: {
					//forceFit: true
				},
				sm: new Ext.grid.RowSelectionModel({singleSelect: true})
				
				//taskGrid.getSelectionModel().selectFirstRow();
				});
			return taskGrid;

		}
	};
}();
