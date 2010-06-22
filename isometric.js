
MAP_SIZE = [100, 50];
CSIZE = 1300;

/* Based on the formulae:
 * xS = (xW-zW)cos(a)s
 * yS = ((xW+zW)sin(a)-yW)s 
 */
var get_coords = function(x, y, z, s){
	return [(x-z) * 0.8944 *s, ((x+z) * 0.4472 - y)*s]
}


var drawHeightField = function(canv, plotf, map){
	var midx = canv.width/3;
	var midy = canv.height/2;

	var inset = (canv.width - CSIZE)/2; //Allows border round edge
	var top = canv.height - CSIZE/2 - inset; //border on top

	var ctx = canv.getContext('2d');
	ctx.fillStyle = "#222";
	var tile_size = Math.sqrt(0.375) * CSIZE;
	
	var heightf = function(x,y){
		var z = map[parseInt(x + y*MAP_SIZE[0])] || {}
		return z.height
		
		}
	
	var indToCoord = function(i,j){
		var c = get_coords(i, heightf(i,j), j, tile_size/MAP_SIZE[0]);
		var d = [inset + midx + c[0], top + c[1], heightf(i,j)];
		if (d[0] && d[1]){
			return d
		} else {
			return;
		}
	}
	
	
	for (var i = 0; i<MAP_SIZE[0]; i++){
		for(var j = 0; j<MAP_SIZE[1]; j++){
			var c = get_coords(i, heightf(i,j), j, tile_size/MAP_SIZE[0]);
			plotf(i, j, 
				indToCoord(i,j),  
				Math.sqrt(5) * ( tile_size/MAP_SIZE[0]),
				indToCoord
				);
		}
	}

}	


var generateMap = function(){
	var map = new Array(MAP_SIZE[0]*MAP_SIZE[1]);
	
	var heightfield = $("#heightfield");
	heightfield[0].width = MAP_SIZE[0];
	heightfield[0].height = MAP_SIZE[1];
	
	//Have to create a frickin canvas
	var hc = $("#hc");
	hc[0].width = MAP_SIZE[0];
	hc[0].height = MAP_SIZE[1];
	var hcc = hc[0].getContext('2d');
	hcc.drawImage(heightfield[0], 0, 0, MAP_SIZE[0], MAP_SIZE[1]);
	var hfdata = hcc.getImageData(0,0,MAP_SIZE[0], MAP_SIZE[1]);
	//console.log(hfdata)
	for (var i = 0; i<map.length; i++){
		var ht = hfdata.data[i*4+1]/50,
			x = 'grass';
		
		if (parseInt(ht*100) < 6.6){
			x = 'sea'
		} else if (i>2*map.length/5 && i < 3*map.length/5){	
			x = 'desert'
		} else{	
			var x = Math.random() > 0.95 ?
				'tree' : Math.random() > 0.95 ?
					Math.random() >0.5 ? 'rock' 
					: 'tree2' 
				: 'grass';
		}		
		map[i] = {
			height:ht,
			terrain:x,
			open:true,
		}
	}


	return map;
}


var imLoad = function(images, callback){
	if (images.length){
		var im = images.pop();
		var img = new Image();
		img.addEventListener('load', function(){imLoad(images, callback)}, false);
		img.src = im;	
	}
	else{
		callback();
	}	
}


$(function(){
	var imgs = [];
	$('img').each(function(){
		imgs.push(this.src);
	});
	
	imLoad(imgs, function(){
		var canv = $("#isocanv")[0];
		var ctx = canv.getContext('2d');
		ctx.fillStyle = "#eee";
		ctx.fillRect (0, 0, screen.width, screen.height);
	
		var MAP = generateMap();
			
		var point = function(x, y, c, s, toc){
			//
			// c n
			// b o
			
			
			var n = toc(x+1, y)
			var b = toc(x, y+1);
			var o = toc(x+1, y+1);
			var terr = MAP[parseInt(x + y*MAP_SIZE[0])]['terrain'];
			if (terr == 'sea'){
				ctx.fillStyle = "#000099";
			}else {
				ctx.fillStyle = "#009900";
				if (b){
					var cb = plib.v3.normalise(plib.v3.sub(b, c));
					var cn = plib.v3.normalise(plib.v3.sub(n, c));
					var col = plib.v3.normalise(plib.v3.cross(cb, cn));
					if (terr == 'desert'){
						ctx.fillStyle = "rgb("+ parseInt(col[0]*2550 +140) + ", " + parseInt(col[0]*2550 +140) + ",0)";
					} else{
						ctx.fillStyle = "rgb(0, " + parseInt(col[0]*2550 +100) + ",0)";
					}	
				}
			}	
			ctx.beginPath();
			
			

			ctx.moveTo(n[0], n[1]);
			
			if (c){
				ctx.lineTo(c[0], c[1]);
			};

			if(b)
				ctx.lineTo(b[0], b[1]);
			
			if(o)
				ctx.lineTo(o[0], o[1]);
			
			
			ctx.closePath();
			ctx.fill();			
			
			
			var m = $('#' +terr)
			
			
			if (m.is('*')){
				m = m[0];
				ctx.drawImage(
					m,
					c[0] - s/2, c[1] - s * (m.height/m.width) *0.5,
					s, s * m.height/m.width
					);
			//ctx.fillRect(c[0], c[1], 1, 1);	
			}
			
		}
	
			
		
		drawHeightField(canv, point, MAP);
	});
});



