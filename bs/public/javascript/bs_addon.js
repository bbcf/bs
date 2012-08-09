/**
 * Event launched after user clicked on a button to call an operation.
 * @param node : the node user clicked on.
 * @param redirection : where the form is displayed.
*/

function bs_make_form(node, redirection){
    window.location = redirection + '?id=' + node.id;
};

