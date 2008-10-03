MaybeLater.ProjectTree = Ext.extend(Tree.TreePanel, {

	initComponent: function() {
		Ext.apply(this, {
			useArrows:true,
			autoScroll:true,
			animate:true,
			enableDD:true,
			containerScroll: true, 
			loader: new Tree.TreeLoader({
			    dataUrl:'get-nodes.php'
			}),

			region: 'center'
		});
		MaybeLater.ProjectTree.superclass.initComponent.call(this);
	},

});


// register the App.BookDetail class with an xtype of bookdetail
Ext.reg('projectTree', MaybeLater.ProjectTree);