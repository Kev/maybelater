/**MaybeLater.TaskDetails = Ext.extend(Ext.Panel, {
	tplMarkup: [
		'Name: <a href="{DetailPageURL}" target="_blank">{name}</a><br/>',
		'Priority: {priority}<br/>',
		'Severity: {severity}<br/>',
		'Description: {description}<br/>'
	],
	startingMarkup: 'No task selected.',


	initComponent: function() {
		this.tpl = new Ext.Template(this.tplMarkup);
		Ext.apply(this, {
			bodyStyle: {
				background: '#ffffff',
				padding: '7px'
			},
			html: this.startingMarkup,
			region: 'south'
		});
		MaybeLater.TaskDetails.superclass.initComponent.call(this);
	},
	updateDetails: function(data) {
		this.tpl.overwrite(this.body, data);		
	}
});*/

MaybeLater.TaskDetails = Ext.extend(Ext.FormPanel, {

	initComponent: function() {
		Ext.apply(this, {
			columnWidth: 0.4,
            labelWidth: 90,
            title:'Task details',
            defaults: {width: 140},	// Default config options for child items
            defaultType: 'textfield',
            autoHeight: true,
            bodyStyle: Ext.isIE ? 'padding:0 0 5px 15px;' : 'padding:10px 15px;',
            border: true,
			frame: true,
            style: {
                "margin-left": "10px", // when you add custom margin in IE 6...
                "margin-right": Ext.isIE6 ? (Ext.isStrict ? "-10px" : "-13px") : "0"  // you have to adjust for it somewhere else
            },
            items: [{
                fieldLabel: 'Name',
                name: 'name'
            },{
                fieldLabel: 'Description',
                name: 'description',
				xtype: 'textarea'
            },{
                fieldLabel: 'Priority',
                name: 'priority'
            },{
	            xtype: 'datefield',
	            fieldLabel: 'Due',
	            name: 'dueDate'
	        },{
                xtype: 'datefield',
                fieldLabel: 'Start',
                name: 'startDate'
            }],
			buttons: [{
			    text: 'Save'
			}/*,{
			    text: 'Cancel'
			}*/],
			
			region: 'south'
		});
		MaybeLater.TaskDetails.superclass.initComponent.call(this);
	},
	updateDetails: function(record) {
		this.getForm().loadRecord(record);		
	}
});

Ext.reg('taskDetails', MaybeLater.TaskDetails);