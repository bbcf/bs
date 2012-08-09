/**
* Initialize the buttons to show the form
* @param root : the html node to attach the buttons to
* @param operations : the JSON operations comming from bs application
*/
function bs_make_buttons(root, operations){
    var cont = dojo.create('div', {}, root);
    
    var ops_container = new dijit.layout.ContentPane({
        title: "Operations",
        id:'tab_ops'
    }, cont);
    
  
    var menu = new dijit.Menu({colspan : 1,
			       style : {width : '10em'}});
    var c = operations.childs;
    var l = c.length;
    for(var i=0;i<l;i++){
        bs_add_child(menu, c[i]);
    }
    menu.placeAt('tab_ops');
};

/**
* Recursivly add childs to the root menu
* @param parent : the html menu to attach the current node
* @param node : the current node
*/
function bs_add_child(parent, node){
    var c = node.childs
    if(c){
	var l = c.length;
	// node has childs (build a menu & add childs to it)
	var m = new dijit.Menu({});
	for(var i=0;i<l;i++){
            bs_add_child(m, c[i]);
        }
        
	var p = new dijit.PopupMenuItem({label : node.key,
					 popup : m
					});
        parent.addChild(p);
    } else {
        // it's the end (must connect an event)                                                        
        var ctx = this;
        var m = new dijit.MenuItem({label : node.key,
				    onClick : function(e){
					bs_make_form(node, bs_redirect);
					dojo.stopEvent(e);
				    }});
        parent.addChild(m);
    }
};


require(["dojo/parser", "dijit/layout/BorderContainer", "dijit/Menu", "dijit/MenuItem", "dijit/PopupMenuItem", "dijit/layout/ContentPane"]);


require(["dojo/dom", "dojo/domReady!"], function(dom){
    var ops = dom.byId('bs_operations');
    try {
	if(!bs_operations_path) throw 'You must define `bs_operations_path` variable.'
	if(!ops) throw 'You must have a div with id `bs_operations`.'
	if(!bs_redirect) throw 'You must define `bs_redirect` variable.'
	if(!bs_make_form) throw 'You must define `bs_make_form` function.'

	bs_make_buttons(ops, bs_operations_path);
    } catch(err){
	console.error(err);
    }

});
