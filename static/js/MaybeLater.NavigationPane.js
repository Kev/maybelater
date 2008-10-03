MaybeLater.NavigationPane = function() {
	var navigationPane;
	return {
        create: function(dataStore, region) {
			return new Ext.Panel({region: region});
		}
	};
}();