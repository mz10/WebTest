var Simplemde;

function editor(el) {
    function vlozTabulku(editor) {
        var cm = editor.codemirror;
        var tabulka = "| | | |\n|-|-|-|\n| | | |\n| | | |";
        cm.replaceSelection(tabulka);
    }

    function vlozZnaky(editor, znakPred, znakPo) {
        var cm = editor.codemirror;
        var vybranyText = znakPred + cm.getSelection() + znakPo;
        cm.replaceSelection(vybranyText);
    }

    function vlozZnak(editor,text) {
        var cm = editor.codemirror;
        var vybranyText = text + cm.getSelection();
        cm.replaceSelection(vybranyText);
    }

    Simplemde = new SimpleMDE({  
        element: document.getElementById(el),
        spellChecker: false,
        autofocus: true,
        //podpora MathJax v nahledu
        previewRender: function(plainText) {
            var preview = document.getElementsByClassName("editor-preview-side")[0];
            preview.innerHTML = this.parent.markdown(plainText);
            preview.setAttribute('id','editor-preview')
            mathjax();
            return preview.innerHTML;
        },
        toolbar: [
        {
            name: "preview",
            action: SimpleMDE.togglePreview,
            className: "fa fa-eye no-disable",
            title: "Náhled v HTML",
        }, 
        {
            name: "side-by-side",
            action: SimpleMDE.toggleSideBySide,
            className: "fa fa-columns no-disable no-mobile",
            title: "Ukázat kód i náhled",
        },
        {
            name: "fullscreen",
            action: SimpleMDE.toggleFullScreen,
            className: "fa fa-arrows-alt no-disable no-mobile",
            title: "Celá obrazovka",
        },
        "|",           
        {
            name: "bold",
            action: SimpleMDE.toggleBold,
            className: "fa fa-bold",
            title: "Tučné",
        },
        {
            name: "italic",
            action: SimpleMDE.toggleItalic,
            className: "fa fa-italic",
            title: "Kurzíva",
        },       
        {
            name: "strikethrough",
            action: SimpleMDE.toggleStrikethrough,
            className: "fa fa-strikethrough",
            title: "Přeškrknuté"
        },
        {
            name: "code",
            action: SimpleMDE.toggleCodeBlock,
            className: "fa fa-code",
            title: "Kód"
        },        
        {
            name: "heading",
            action: SimpleMDE.toggleHeadingSmaller,
            className: "fa fa-header",
            title: "Vytvořit nadpis",
        },
        "|",
        {
            name: "link",
            action: SimpleMDE.drawLink,
            className: "fa fa-link",
            title: "Odkaz",
        },
        {
            name: "image",
            action: SimpleMDE.drawImage,
            className: "fa fa-picture-o",
            title: "Obrázek",
        },
        "|",
        {
            name: "unordered-list",
            action: SimpleMDE.toggleUnorderedList,
            className: "fa fa-list-ul",
            title: "Odrážky",
        },
        {
            name: "ordered-list",
            action: SimpleMDE.toggleOrderedList,
            className: "fa fa-list-ol",
            title: "Číslování",
        },
        {
            name: "table",
            action: vlozTabulku,
            className: "fa fa-table",
            title: "Tabulka"
        },
        "|",
        {
            name: "undo",
            action: SimpleMDE.undo,
            className: "fa fa-undo no-disable",
            title: "Vrátit"
        },
        {
            name: "redo",
            action: SimpleMDE.redo,
            className: "fa fa-repeat no-disable",
            title: "Vrátit zpět"
        },
        "|",
        {
            name: "quote",
            action: SimpleMDE.toggleBlockquote,
            className: "fa fa-quote-left",
            title: "Citace",
        },
        {
            name: "horizontal-rule",
            action: SimpleMDE.drawHorizontalRule,
            className: "fa fa-minus",
            title: "Vodorovný oddělovač"
        },
        "|",
        {
            name: "guide",
            action: "https://simplemde.com/markdown-guide",
            className: "fa fa-question-circle",
            title: "Nápověda",
        }, 
        {
            name: "zavorky",
            action: function(editor) {vlozZnaky(editor,"[", "]")},
            className: "fa zavorky",
            title: "Vložit závorky",
        },  
        {
            name: "zavorkySl",
            action: function(editor) {vlozZnaky(editor,"{", "}")},
            className: "fa zavorkySl",
            title: "Vložit závorky",
        },
        {
            name: "dolar",
            action: function(editor) {vlozZnak(editor,"$")},
            className: "fa dolar",
            title: "Vložit proměnnou",
        },               
        {
            name: "alfa",
            action: function(editor) {vlozZnak(editor,"α")},
            className: "fa alfa",
            title: "Znak alfa",
        }, 
        {
            name: "beta",
            action: function(editor) {vlozZnak(editor,"β")},
            className: "fa beta",
            title: "Znak beta",
        }, 
        {
            name: "gama",
            action: function(editor) {vlozZnak(editor,"γ")},
            className: "fa gama",
            title: "Znak gama",
        }, 
        {
            name: "pi",
            action: function(editor) {vlozZnak(editor,"π")},
            className: "fa pi",
            title: "Znak pí",
        }, 
        {
            name: "mi",
            action: function(editor) {vlozZnak(editor,"µ")},
            className: "fa mi",
            title: "Znak mí",
        },
        {
            name: "omega",
            action: function(editor) {vlozZnak(editor,"Ω")},
            className: "fa omega",
            title: "Znak omega",
        },
        {
            name: "sipka",
            action: function(editor) {vlozZnak(editor,"→")},
            className: "fa sipka",
            title: "Vložit šipku",
        },
        {
            name: "nerovnost",
            action: function(editor) {vlozZnak(editor,"≠")},
            className: "fa nerovnost",
            title: "Znak nerovnost",
        },
    ],
    });
}