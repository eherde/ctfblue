function escapeHTML(form){
			//alert('hello');
			var unsafe = form.user.value;
			var safe = unsafe.replace(/&/g, "&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"quot;").replace(/'/g,"&#039;");

		}