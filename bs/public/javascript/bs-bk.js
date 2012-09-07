/**
 * BioScript javascript.
 * Include this where you want to render the BS form.
 * You have to define javascript variable before
 * Page is loaded :
 * required :
 * @var : bs_server_url : the server adress where BioSript run on
 *
 * Some javascript hooks are available:
 * @func : bs_before_submit() : called before the form is submitted
 * @func : bs_after_submit() : called after the form is submitted
 * @func : bs_after_validation(data) : called after the validation, data
 * is the response of the validation
 *
 */



window.onload = function() {
    bs_variable_defined(bs_server_url);
    var ins = $('div.bs_form').children('form').find('input[type=file]');
    if (ins.length > 0){
        bs_hack_file_upload();
    } else {
        bs_hack_submit();
    }
};

function bs_jsonp_cb(data){
    if(data['validation'] == 'success'){
        console.log(data);
    }
    else if(data['validation'] == 'failed'){
        $('div.bs_form').children('form').replaceWith(data['widget']);
        bs_hack_submit();
    }

    bs_if_exist_call(bs_after_validation, data);

}


var f_input = '<div class="row fileupload-buttonbar">' +
    '<div class="span7">' +
    '<!-- The fileinput-button span is used to style the file input field as button -->' +
    '<span class="btn btn-success fileinput-button">' +
    '<i class="icon-plus icon-white"></i>' +
    '<span>Add files...</span>' +
    '<input type="file" name="files[]" multiple></span>' +
    '<button type="submit" class="btn btn-primary start">' +
    '<i class="icon-upload icon-white"></i>' +
    '<span>Start upload</span>' +
    '</button><button type="reset" class="btn btn-warning cancel"><i class="icon-ban-circle icon-white"></i><span>Cancel upload</span></button><button type="button" class="btn btn-danger delete"><i class="icon-trash icon-white"></i><span>Delete</span></button><input type="checkbox" class="toggle"></div><div class="span5 fileupload-progress fade"><div class="progress progress-success progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100"><div class="bar" style="width:0%;"></div></div><div class="progress-extended">&nbsp;</div></div></div><div class="fileupload-loading"></div><br><table role="presentation" class="table table-striped"><tbody class="files" data-toggle="modal-gallery" data-target="#modal-gallery"></tbody></table>'
/**
 * File upload are managed with the
 * JQuery-File-Upload (https://github.com/blueimp)
 */
function bs_hack_file_upload(){
    var bs_form = $('div.bs_form');


    $(bs_form).fileupload({
        dataType: 'json',
        autoUpload: false,
        add : function(e, data){
            $('#submit').one('click', function () {
                data.submit();
                    });
                }
    });

    $('#fileupload').bind('fileuploadsend', function (e, data) {
        data.formData.push({
            name: 'parameter_name',
            value: 'parameter_value'
        });
    });

//    $(bs_form).bind('fileuploadadd',function(e,data){
//        console.log("biind");
//        console.log(data);
//        var queued=parseInt($('.filesQueued').text());//queued files counter
//        queued+=data.files.length;//number
//        $('.filesQueued').html(queued);//update counter
//        $(bs_form).on('submit',false);//disabling submit event
//        $('#submit').first().on('click',function(){//set click event
//            if(parseInt($('.filesQueued').text())>0){//if queued files
//                //$.each(data.files,function(k,v){alert(k+' '+v)});
//                console.log('some files');
//                data.submit();//submit them
//            } else{//if none
//                console.log("no files");
//                $(bs_form).on('submit',true);//enabling submit
//                $(bs_form).submit();//usual submit of target form
//            }
//        });
//    });



}


/**
 *  Alter form submit : do a JSONP GET instead
 */
function bs_hack_submit(){
    $('div.bs_form').children('form').submit(function(){

        /* fetch form id from form */
        var fid = jQuery.parseJSON($('div.bs_form').find('input#pp').val())['id'];
        var pdata = $(this).serialize() + '&id=' + fid + '&callback=bs_jsonp_cb';
        /* submit query */
        bs_if_exist_call('bs_before_submit');
        $.ajax({
            url: bs_server_url + '/plugins/validate?' + pdata,
            crossDomain: true
        });
        bs_if_exist_call('bs_after_submit');
        return false;
    });
}



function bs_after_validation(data){
    console.debug('after validate');
    console.debug(data);
}


/**
 * Function called to show the bs form.
 * @param fid - the form identifier
 */
function bs_show_form(fid){
    if_exist_call(bs_before_show_form);
    if_exist_call(bs_after_show_form);
 }


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
    var cont = document.createElement('DIV');
    cont.id = "tab_ops";
    
    var mb = document.createElement('UL');
    mb.id = "menu-bar";
    var op = bs_create_element("Operations");
    
    
    
    var c = operations.childs;
    if(c){
	var l = c.length;
	var u = document.createElement("UL");
	for(var i=0;i<l;i++){
            bs_add_child(u, c[i]);
	}
	op.appendChild(u);
    }
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




//
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
