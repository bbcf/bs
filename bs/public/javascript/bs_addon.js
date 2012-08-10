/**
 * Event launched after user clicked on a button to call an operation.
 * @param node : the node user clicked on.
 * @param redirection : where the form is displayed.
*/

function bs_make_form(node, redirection){
    window.location = redirection + '?id=' + node.id;
};


/** function called after form sumbmission
* @param id : operation id
* @param task_id : job id
*/
function after_submission_hook(id, task_id, redirection){
    if (top === self){ // no frame => redirection ?? 
	window.location = redirection + '?task_id=' + task_id;
    } else { // frame => call parent function
	parent.after_submission_hook(id, task_id);
    }
}