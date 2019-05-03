// Script relatif à l'ajout de stock

$(document).ready(function () {

    /**************************************************************************
     *
     *                                      Gestion ADD REMOVE Formset 
     *
     ***************************************************************************/

    index_form = function (fset, index) {

        $(fset).find(':input').each(function () {
            var name = $(this).attr('name').replace(new RegExp('(\_\_prefix\_\_|\\d)'), index);
            var id = 'id_' + name;
            $(this).attr({
                'name': name,
                'id': id
            });
        });

        $(fset).find('label').each(function () {
            var newFor = $(this).attr('for').replace(new RegExp('(\_\_prefix\_\_|\\d)'), index);
            var id = 'label_' + newFor;
            $(this).attr({
                'id': id,
                'for': newFor
            });
        });

    }

    reindex_formset = function (formset_zone) {

        var formset = $(formset_zone).find('.formrow');
        for (var cpt = 0; cpt < formset.length; cpt++) {
            index_form(formset[cpt], cpt);
        };

        $("#id_form-TOTAL_FORMS").val(parseInt(cpt));

    };



    /**************************************************************************
     *
     *                               Gesion Des evenements formulaire
     *
     ***************************************************************************/


    set_event = function () {
        //Bind le(s) bt delete sorte
        //$(".bt_rm_sorte").on('click', function () {
        $(document).on('click', '.bt_rm_sorte', function () {
            $(this).parents(".formrow").remove();
            reindex_formset("#corps");
        });
    };

    $("#bt_add_sorte").on('click', function () {

        //Copy form
        var divlot = $("#rlot:first").clone(true);

        var trashDiv = document.createElement('div');
        trashDiv.className = 'col-md-1 ml-auto btn btn-sm bt_rm_sorte';
        var innerElement = document.createElement('i');
        innerElement.className = 'fa fa-trash';
        trashDiv.appendChild(innerElement);

        divlot.find("#foro").append(trashDiv);
        //var c = divlot.childNodes;
        //console.log(c);
        //c[0].append(trashDiv);
        //divlot.append(trashDiv);
        divlot.appendTo($("#corps"));
        //trashDiv.appendTo($("#corps"));

        reindex_formset("#corps");

    });

    set_event();

});