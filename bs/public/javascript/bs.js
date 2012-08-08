/**
* Initialize the buttons to ge the form
* @param root : the html node to attach the buttons to
* @ operations : the JSOn operations comming from bs application
*/
function display_operations(root, operations){
    var cont = dojo.create('div', {}, root);
    
    var ops_container = new dijit.layout.ContentPane({
        title: "Operations",
        id:'tab_ops'
    }, cont);
    
  
    var menu = new dijit.Menu({colspan : 1,
			       style : {width : '10em'}
			      });

    var c = operations.childs;
    var l = c.length;
    for(var i=0;i<l;i++){
        menu_add_child(menu, c[i]);
    }
    menu.placeAt('tab_ops');
};

/**
* Add children to the operation menu
* @param parent : the html menu to attach the current node
* @ parm node : the current node
*/
function menu_add_child(parent, node){
    var c = node.childs
    if(c){
	var l = c.length;
	// node has childs (build a menu & add childs to it)
	var m = new dijit.Menu({});
	for(var i=0;i<l;i++){
            menu_add_child(m, c[i]);
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
					button_event(node);
					dojo.stopEvent(e);
				    }});
        parent.addChild(m);
    }
};

/**
* Event launched after user clicked on a button to call an operation
* @param node : the node he clicked on
*/

function button_event(node){
    var path = window.location.pathname;
    path = path.replace("/form/list", "/form/index");
    window.location = path + '?id=' + node.id;
};

require(["dojo/parser", "dijit/layout/BorderContainer", "dijit/Menu", "dijit/MenuItem", "dijit/PopupMenuItem", "dijit/layout/ContentPane"]);


require(["dojo/dom", "dojo/domReady!"], function(dom){
    display_operations(dom.byId('operations'), operations_path);
});
