/**
* Create a menu element.
*/
function bs_create_element(name){
    var el = document.createElement('LI');
    var l = document.createElement('A');
    l.innerHTML = name;
    l.href='#';
    el.appendChild(l);
    return el;
}


/**
* Initialize the buttons to show the form
* @param root : the html node to attach the buttons to
* @param operations : the JSON operations comming from bs application
*/
function bs_make_buttons(root, operations){
    var cont = document.createElement('DIV');
    cont.id = "tab_ops";
    
    var mb = document.createElement('UL');
    mb.id = "menu-bar";
    var op = bs_create_element("Operations");
    
    
    
    var c = operations.childs;
    var l = c.length;
    var u = document.createElement("UL");
    for(var i=0;i<l;i++){
        bs_add_child(u, c[i]);
    }
    op.appendChild(u);
    mb.appendChild(op);
    cont.appendChild(mb);
    root.appendChild(cont);

};

/**
* Recursivly add childs to the root menu
* @param parent : the html menu to attach the current node
* @param node : the current node
* @param bool : if parent is the root.
*/
function bs_add_child(parent, node){
    
    var op = bs_create_element(node.key);
    

    var c = node.childs
    if(c){     // recursivly add childs
	var l = c.length;
	var u = document.createElement("UL");
	for(var i=0;i<l;i++){
            bs_add_child(u, c[i]);
        }
	op.appendChild(u);
    } else {   // it's the end (must connect an event)                                                        
        var ctx = this;
	op.onclick = function(){
	    bs_make_form(node, bs_redirect);
	
	}
    }
    parent.appendChild(op);
};


window.onload = function() {
    var ops = document.getElementById('bs_operations');
    try {
	if(!bs_operations_path) throw 'You must define `bs_operations_path` variable.'
	if(!ops) throw 'You must have a div with id `bs_operations`.'
	if(!bs_redirect) throw 'You must define `bs_redirect` variable.'
	if(!bs_make_form) throw 'You must define `bs_make_form` function.'
	
	bs_make_buttons(ops, bs_operations_path);
    } catch(err){
	console.error(err);
    }
}
