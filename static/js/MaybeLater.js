/** MaybeLater Kevin Smith 2008 GPL.
 */

/*global Ext, Application */

Ext.BLANK_IMAGE_URL = '/extplayground/ext-2.1/resources/images/default/s.gif';
Ext.ns('MaybeLater');

MaybeLater.Application = function() {
    //Private 
    var btn1;
    var privVar1 = 11;
    
    var btn1Handler = function(button, event) {
            alert('privVar1=' + privVar1);
            alert('this.btn1Text=' + this.btn1Text);
        };
    
    
    return {
        //Public
        btn1Text: 'Button 1',
        
        init: function() {
        	var navigation = MaybeLater.NavigationPane.create('west');
			var dataStore = MaybeLater.Data.createStore();
		    var taskList = MaybeLater.TaskList.create(dataStore, 'center');
			var taskDetails = new MaybeLater.TaskDetails();
			
			taskList.getSelectionModel().on('rowselect', function(sm, rowIdx, record) {
					taskDetails.updateDetails(record);
				});
			

		    var viewport = new Ext.Viewport({
		        layout:'border',
		        items:[
		            /*new Ext.BoxComponent({ 
		                region:'north',
		                el: 'header',
		                height:32
		            }),*/
		            navigation,
		            taskList,
					taskDetails
		         ]
		    });
                            
            
        }
    };
}(); 

