(function($){
    var plugin = this;
    var bs_namespace = 'bioscript';
    /* default settings */
    var settings = {
        operation_list: {},
        root_name: 'BioScript operations',
        bs_server_url: 'http://localhost:8080/',
        form_selector: 'div.bs_form',
        validation_url: 'htpp://localhost:8080/validation',
        fetch_url: 'htpp://localhost:8080/fetch',
        bs_form_container_selector: '#bs_form_container',
        show_plugin: false,
        validation_successful: false,
        fsizemax: 255,
        app: '',
        getcsrftoken: function(){
            return $('meta[name="csrf-token"]').attr('content');
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
                if (settings.bs_server_url.indexOf('/', settings.bs_server_url.length - 1) == -1){
                    settings.bs_server_url += '/';
                }
                if(!data){
                    $(this).data(bs_namespace,{
                        target : $this,
                        oplist : settings.operation_list.plugins,
                        rname : settings.root_name,
                        plugin : settings.show_plugin,
                        bsurl : settings.bs_server_url,
                        fselector : settings.form_selector,
                        vurl: settings.validation_url,
                        vsuccess : settings.validation_successful,
                        geturl: settings.fetch_url,
                        bsform: settings.bs_form_container_selector,
                        fsizemax: settings.fsizemax,
                        app: settings.app,
                        csrf: settings.getcsrftoken
                    });
                    data = $this.data(bs_namespace);
                    // $.ajaxSetup({
                    //     beforeSend: function(xhr) {
                    //     xhr.setRequestHeader('X-CSRF-Token', $('meta[name="csrf-token"]').attr('content'));
                    // }});
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
            data.target.append($('<ul/>', {id : 'bs_menubar'}).append(el));
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
            var $this = $(this);
            var data = $this.data(bs_namespace);
            $(el).click(function(){
                if (data.plugin){
                    data.plugin(el.id);
                } else {
                    _incall($this, 'show_plugin', el.id);
                }
            });
        },

        /**
         * hack the submit button of the BioScript
         * form to perform a JSONP query instead
         */
        hack_submit : function(){
            var $this = $(this);
            var data = $this.data(bs_namespace);
            var bs_url = data.bsurl;
            var fselector = data.fselector;
            var fsizemax = data.fsizemax;
            $(fselector).children('form').submit(function(e){
                e.preventDefault();
                /* fetch form id from form */
                //var fid = jQuery.parseJSON($(fselector).find('input#pp').val())['id'];

//    $(':file').change(function(){
//        var file = this.files[0];
//        name = file.name;
//        size = file.size;
//        type = file.type;
//        //your validation
//    });
            var waitdiv = $('<div class="loading-wrap"><span class="triangle1"></span><span class="triangle2"></span><span class="triangle3"></span></div>');
            waitdiv.css('left', $(this).find('input').width() + 'px');
            waitdiv.css('top', -$(this).find('input').height() + 'px');
            $(this).append(waitdiv);



            /* build form data objet to upload files if any */
            var formData = new FormData();
            var files = $(':file');
            for(var i = 0; i < files.length; i++) {
                var fid = files[i].name;
                var fs = files[i].files;
                for(var j=0;j<fs.length;j++){
                    var f = fs[j];
                    if(f){
                        // file size max
                        if (f.size > fsizemax * 1000000 ){
                            alert('File is too big. You cannot upload files greater than '+ fsizemax + ' Mo.');
                            $('.loading-wrap').remove();
                            return false;
                        }
                        formData.append(fid, f);
                    }
                }
            }
            /* get data from form */
            var pdata = $(this).serializeArray();
            $.each(pdata, function(i, v){
                formData.append(v.name, v.value);
            });
            /* disable the form button and show waiting stuff */
            var fo = $(this).find('#submit');
            fo.attr('disabled', true);
            fo.addClass('waiting');

            /* submit query */
            $.ajax({
                    url: bs_url + 'plugins/validate',
                    type : 'POST',
                    data : formData,
                    processData:false,
                    contentType:false
                    }).done(function(d) {
                        fo.attr('disabled', false);
                        $('.loading-wrap').remove();
                        _incall($this, 'jsonp_callback', [d]);
                    }).error(function(error){
                        fo.attr('disabled', false);
                        $('.loading-wrap').remove();
                        console.error("POST ERROR");
                        console.error(error);
                    });
                    return true;
                });
        },

        /**
         * After form submit, a json is sent back from
         * BioScript server
         */
        jsonp_callback : function(jsonp){
            var $this = $(this);
            var data = $this.data(bs_namespace);
            if (jsonp){
                jsonp = $.parseJSON(jsonp);
                var val = jsonp.validation;
                if (val == 'failed'){
                    // validation failed : display the form with errors
                    var fselector = data.fselector;
                    $(fselector).children('form').replaceWith(jsonp.widget);
                    _incall($this, 'hack_submit');
                } else if(val == 'success'){
                    // validation passed
                    if(jsonp.error){
                        // but there is an error
                        alert(jsonp.error);
                    } else {
                        if (data.vsuccess){
                            data.vsuccess(jsonp.plugin_id, jsonp.task_id, jsonp.plugin_info);
                        } else {
                            _incall($this, 'validation_success', [jsonp.plugin_id, jsonp.task_id, jsonp.plugin_info, jsonp.app]);
                        }
                    }

                } else {
                    console.error("Callback with wrong data");
                    console.error(data);
                }
            } else {
                console.error("Callback with no data.");
            }
        },

        show_plugin: function(plugin_id){
            var $this = $(this);
            var data = $this.data(bs_namespace);
            var pdata = data.app;
            $.ajax({
                'url' : data.geturl + '?oid=' + plugin_id,
                'dataType': 'html',
                crossDomain: true,
                'beforeSend': function(xhr) {
                    xhr.setRequestHeader('X-CSRFToken', data.csrf());
                },
                type : 'POST',
                datatype:'json',
                data : pdata,
                'success': function(r){
                    _incall($this, 'toggle_bs_form',[plugin_id, r]);
                    _incall($this, 'hack_submit');
                   //$('body').bioscript(form_options).bioscript('hack_submit');
                }
            });
         },

         validation_success: function(plugin_id, task_id, plugin_info, app){
            var $this = $(this);
            var data = $this.data(bs_namespace);
            u = data.vurl + '?task_id=' + task_id + '&plugin_id=' + plugin_id;
            var pdata = app;
            if (plugin_info){
                pdata['plugin_info'] = plugin_info;
            }
            $.ajax({
                'url': u,
                type: 'POST',
                datatype: 'json',
                data: pdata,
                'beforeSend': function(xhr) {
                    xhr.setRequestHeader('X-CSRFToken', data.csrf());
                },
                'success': function(r){
                    _incall($this, 'toggle_bs_form', [plugin_id]);
                }
            });
         },

         toggle_bs_form: function(plugin_id, form_data){
            var $this = $(this);
            var data = $this.data(bs_namespace);
            var $cont = $(data.bsform);
            var showed = $cont.attr('showed');
            if (showed == plugin_id){
                $cont.html('');
                $cont.hide('normal');
                $cont.attr('showed', '');
            } else if (showed){
                $cont.html(form_data);
                $cont.attr('showed', plugin_id);
            } else {
                $cont.html(form_data);
                $cont.attr('showed', plugin_id);
                $cont.show('slow');
            }
        }
    };

    $.fn[bs_namespace] = function(method){
        if(methods[method]){
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if ( typeof method === 'object' || !method){
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method "' + method + '" does not exist on jQuery.' + bs_namespace + '.');
        }
    };
})(jQuery);


function bs_jsonp_cb(data){
    $('body').bioscript({'jsonp_data': data}).bioscript('jsonp_callback', data);
}


function progress_handler(e){
    console.log(e);
}