/* ------------------------------------------------------------------------
- A Custom JS File uses JSXGraph - https://jsxgraph.uni-bayreuth.de/wp/about/index.html
--------------------------------------------------------------------------*/
var turtle = null;
var alpha = 0;

function load_map()
{
   var width = screen.width * 0.45;
    var brd = JXG.JSXGraph.initBoard('box',{ boundingbox: [-width, 300, width, -300], keepaspectratio:true });
    turtle = brd.create('turtle',[0, 0], {strokeOpacity:0.5});
    turtle.setPenSize(3);
    turtle.right(90);
}

// TURTLE EXAMPLE
function drawmap() {
   turtle.forward(2);
   if (Math.floor(alpha / 360) % 2 === 0) {
      turtle.left(1);        // turn left by 1 degree
   } else {
      turtle.right(1);       // turn right by 1 degree
   }

   alpha += 1;
   if (alpha < 1440) {  // stop after two rounds
       setTimeout(drawmap, 20); 
   }
}
function draw_square(size, pen_colour =false, fill_colour = false){
   if (pen_colour){
      turtle.setPenColor(pen_colour)
   }if (fill_colour){    
      turtle.setHighlightPenColor(fill_colour)
   }for (var i = 0; i < 4; i++){
      turtle.forward(size)
      turtle.right(90)
   }
    return
}
function go_to(x,y,heading = 0){
   turtle.penUp()
   turtle.setPos(x,y)
   turtle.penDown()
   turtle.lookTo(heading)
   return
}
function draw_victim(victim_type, x, y){
   turtle.setPenSize(1)
   if (victim_type.toLowerCase() == 'harmed'){
      go_to(x, y)
      draw_square(15, (255,90,90), (255,90,90))
      go_to(x +2, y - 20)
      turtle.setPenColor((0,0,0))
      turtle.write('H', font=('Calibri', 15, 'italic'))
   }
}
load_map();
draw_victim('harmed', 0, 0);