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
    console.log('submitted with id : ' + task_id);
    var ifr = document.getElementById("ifr");
    ifr.src = redirection + '?id=' + node.id;
}