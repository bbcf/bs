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
                var ul = $('<ul/>');
                $.each(children, function(index, child){
                    _incall($this, '_add_childs', [ul, child]);
                });
                el.append(ul);
            }
            // append all to the target
            data.target.append($('<div/>', {id : 'bs_operations_container'}).append($('<ul/>', {id : 'bs_menubar'}).append(el)));
        },

        _create_menu_element : function(name){
            return $('<li>').append('<a href="#">' + name +'</a>');
        },

        _add_childs : function(parent, child){
            var $this = $(this);
            var el = _incall($this, '_create_menu_element', child.key);
            var children = child.childs;
            if (children){
                var ul = $('<ul/>');
                $.each(children, function(index, child){
                    _incall($this, '_add_childs', [ul, child]);
                });
                el.append(ul);
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
            $.error('Method ' + method + 'does not exist on jQuery.' + bs_namespace + '.');
        }
    }
})(jQuery);