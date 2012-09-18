(function($){
    var plugin = this;
    var bs_namespace = 'bioscript';
    /* default settings */
    var settings = {
        operation_list : {},
        root_name : 'BioScript operations',
        show_plugin : function(plugin_id){
            alert('Click on plugin ' + plugin_id + ' .');
        }
    };
    /* inside call */
    var _incall = function(that, method, args){
        if (!(args instanceof Array)){
            args = [args];
        }
        return methods[method].apply(that, args);
    };
    /* plugin methods */
    var methods = {
        init : function(options){
            return this.each(function(){
                $.extend(settings, options);
                var $this = $(this),
                    data = $this.data(bs_namespace);
                if(!data){
                    $(this).data(bs_namespace,{
                        target : $this,
                        oplist : settings.operation_list.plugins,
                        rname : settings.root_name,
                        plugin : settings.show_plugin
                    });
                    data = $this.data(bs_namespace);
                }
            });
        },
        /**
         * List Operations available in BioScript
         */
        operation_list : function(){
            var $this = $(this);
            var data = $this.data(bs_namespace);
            // create root element
            var el = _incall($(this), '_create_menu_element', data.rname);
            // recursively add children
            var children = data.oplist.childs;
            if(children){
                $.each(children, function(index, child){
                    _incall($this, '_add_childs', [el, child]);
                });
            }
            // append all to the target
            el.appendTo($('<ul/>', {id : 'bs_menubar'})).appendTo($('<div/>', {id : 'bs_operations_container'})).appendTo(data.target);
        },

        _create_menu_element : function(name){
            return $('<li>').append('<a href="#">' + name +'</a>');
        },

        _add_childs : function(parent, child){
            var $this = $(this);
            var el = _incall($this, '_create_menu_element', child.key);
            var children = child.childs;
            if (children){
                $.each(children, function(index, child){
                    _incall($this, '_add_childs', [el, child]);
                });
            } else {
                el.id = child.id;
                _incall($this, '_bind_child', el);
            }
            parent.append(el);
        },

        _bind_child : function(el){
            var data = $(this).data(bs_namespace);
            $(el).click(function(){
                data.plugin(el.id);
            });
        }
    };

    $.fn[bs_namespace] = function(method){
        if(methods[method]){
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if ( typeof method === 'object' || !method){
            return methods.init.apply(this, arguments)
        } else {
            $.error('Method ' + method + 'does not exist on jQuery.tooltip');
        }
    }
})(jQuery);









/**
 * Utility function : check if a variable exist
 * else throw an exception
 * @param v - the variable
 */
function bs_variable_defined(v){
    if(typeof v == "undefined"){
        throw 'Missing javascript variable';
    }
}
/**
 * Utility function : call a function if it exist
 * @param fn - the function
 */
function bs_if_exist_call(fn, data){
    if (typeof fn == 'function'){
        fn(data);
    }
}









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




//window.onload = function() {
//    var ops = document.getElementById('bs_operations');
//    try {
//	if(!bs_operations_path) throw 'You must define `bs_operations_path` variable.'
//	if(!ops) throw 'You must have a div with id `bs_operations`.'
//	if(!bs_redirect) throw 'You must define `bs_redirect` variable.'
//	if(!bs_make_form) throw 'You must define `bs_make_form` function.'
//
//	bs_make_buttons(ops, bs_operations_path);
//    } catch(err){
//	console.error(err);
//    }
//}
