

var ratio = 1.0;
var canvas = null;
var WIDTH;
var HEIGHT;
var img = null;
var boxWidth = 80;
var boxHeight = 50;
// holds all our boxes
var boxes2 = []; 
var canvasValid = false;

function invalidate() {
    canvasValid = false;
}

// Box object to hold data
function Box2() {
    this.x = 0;
    this.y = 0;
    this.w = 1; // default width and height?
    this.h = 1;
    this.fill = '#444444';
}

//Initialize a new Box, add it, and invalidate the canvas
function addRect(x, y, w, h, fill) {
    var rect = new Box2;
    rect.x = x;
    rect.y = y;
    rect.w = w
    rect.h = h;
    rect.fill = fill;
    boxes2.push(rect);
    invalidate();
}

window.onload = function() {
    canvas = document.getElementById("canvas2");

    $("#file_input").change(function(e) {
        var URL = window.webkitURL || window.URL;
        var url = URL.createObjectURL(e.target.files[0]);
        img = new Image();
        img.src = url;
        img.onload = function() {
            drawImage(img);
            boxes2 = [];
            // addRect((img.width/ratio-boxWidth)/2 , (img.height/ratio-boxHeight)/2, boxWidth, boxHeight, 'rgba(220,205,65,0.7)');
        }
        // initDraw(canvas);
    });
}

function drawImage() {
    if (img !== null) {
        var context = canvas.getContext("2d");
        var rect = canvas.getBoundingClientRect();
        var img_width = img.width;
        var img_height = img.height;

        if(img_width > rect.width || img_height > rect.height) {
            
            if(img_width > rect.width) {
                img_width = rect.width;
                ratio = img.width / img_width;
                img_height = img.height / ratio;
            }

            if(img_height > rect.height) {
                img_height = rect.height;
                ratio = img.height / img_height;
                img_width = img.width / ratio;
            }
        }
        context.drawImage(img, 0, 0, img_width, img_height);
    }
}

function drawRect(canvas, x, y, w, h, color='red') {
    var context = canvas.getContext('2d');
    context.beginPath();
    context.rect(x, y, w, h);
    // context.fillStyle = 'yellow';
    // context.fill();
    context.lineWidth = 2;
    context.strokeStyle = color; //'black';
    context.stroke();
}

function randomise() {

    if(img === null) {
        $("#ranerror").text("Take a picture");
        return;
    }

    if(boxes2.length == 0) {
        $("#ranerror").text("Select reference object");
        return;
    }

    var formData = new FormData($('#createform')[0]);
    formData.append("xmin", Math.floor(boxes2[0].x * ratio));
    formData.append("ymin", Math.floor(boxes2[0].y * ratio));
    formData.append("xmax", Math.floor((boxes2[0].x + boxes2[0].w) * ratio));
    formData.append("ymax", Math.floor((boxes2[0].y + boxes2[0].h) * ratio));

    $.ajax({
        url: '/api/randomiser',  //Server script to process data
        type: 'POST',
        data: formData,
        // xhr: function() {  },
        success: function(data) {  
            if(data.size && data.size > 0) {
                for(var i = 0; i < data.size; i++) {
                    $("#randon"+i).html(data.bboxes[i][0]+" - "+data.bboxes[i][1]+" - "+
                                        data.bboxes[i][2]+" - "+data.bboxes[i][3]);

                    drawRect(canvas, Math.floor(data.bboxes[i][0] / ratio), 
                                    Math.floor(data.bboxes[i][1] / ratio), 
                                    Math.floor(data.bboxes[i][2] / ratio - data.bboxes[i][0] / ratio), 
                                    Math.floor(data.bboxes[i][3] / ratio - data.bboxes[i][1] / ratio), 'blue');
                }
                $("#ranerror").text("");
            } else {
                for(var i = 0; i < data.size; i++) {
                    $("#randon"+i).html('');
                }
                $("#ranerror").text("No match found!");
            }
        },
        error: function (jqXHR, textStatus, errorThrown) { $("#ranerror").text(errorThrown); },
        cache: false,
        contentType: false,
        processData: false
    });
}

var mouse = {
    startX: 0,
    startY: 0,
    x: 0,
    y: 0,
};

function initDraw(canvas) {
    var rect = canvas.getBoundingClientRect();
    // console.log(rect);
    // drawRect(canvas, 0, 0, rect.width, rect.height);

    // var mouseIsDown = false;
    var scrollX = window.scrollX;
    var scrollY = window.scrollY;

    function setMousePosition(e) {
        var ev = e || window.event; //Moz || IE
        if (ev.pageX) { //Moz
            mouse.x = ev.pageX - scrollX - rect.x; //+ window.pageXOffset ;
            mouse.y = ev.pageY - scrollY - rect.y; //+ window.pageYOffset ;
        } else if (ev.clientX) { //IE
            mouse.x = ev.clientX - rect.x; //+ document.body.scrollLeft ;
            mouse.y = ev.clientY - rect.y; //+ document.body.scrollTop ;
        }
    };

    canvas.onmousedown = function(e) {
        // mouseIsDown = true;
        drawImage(img);
        setMousePosition(e);
        mouse.startX = mouse.x;
        mouse.startY = mouse.y;
        canvas.style.cursor="crosshair";
    }

    canvas.onmouseup = function(e) {
        setMousePosition(e);
        // mouseIsDown = false;
        drawRect(canvas, mouse.startX, mouse.startY, mouse.x-mouse.startX, mouse.y-mouse.startY);
    }
}

