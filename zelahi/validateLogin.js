function validateLogin() {

		
	var x=documents.forms["login"]["username"].value;
	
	//ensure that a password and email have been entered
	if (x == null || x="") {
		alert("Please enter the required information");
		return false
	}
}
