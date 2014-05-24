function escapeHTML(form){
			//alert('hello');
			var unsafe = document.getElementByTagName("input");
			for(var i = 0; i < unsafe.length; i++) {
				var safe[i] = unsafe[i].replace(/&/g, "&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"quot;").replace(/'/g,"&#039;");
			}
}