
MAP_SIZE = 50;
CSIZE = 900;

/* Based on the formulae:
 * xS = (xW-zW)cos(a)s
 * yS = ((xW+zW)sin(a)-yW)s 
 */
var get_coords = function(x, y, z, s){
	return [(x-z) * 0.8944 *s, ((x+z) * 0.4472 - y)*s]
}


var drawHeightField = function(canv, plotf, map){
	var midx = CSIZE/2;
	var midy = CSIZE/4;

	var inset = (canv.width - CSIZE)/2; //Allows border round edge
	var top = canv.height - CSIZE/2 - inset; //border on top

	var ctx = canv.getContext('2d');
	ctx.fillStyle = "#222";
	var tile_size = Math.sqrt(0.375) * CSIZE;
	
	var heightf = function(x,y){
		var z = map[parseInt(x + y*MAP_SIZE)] || {}
		return z.height
		
		}
	
	var indToCoord = function(i,j){
		var c = get_coords(i, heightf(i,j), j, tile_size/MAP_SIZE);
		var d = [inset + midx + c[0], top + c[1], heightf(i,j)];
		if (d[0] && d[1]){
			return d
		} else {
			return;
		}
	}
	
	
	for (var i = 0; i<MAP_SIZE; i++){
		for(var j = 0; j<MAP_SIZE; j++){
			var c = get_coords(i, heightf(i,j), j, tile_size/MAP_SIZE);
			plotf(i, j, 
				indToCoord(i,j),  
				Math.sqrt(5) * ( tile_size/MAP_SIZE),
				indToCoord
				);
		}
	}

}	


var generateMap = function(){
	var map = new Array(MAP_SIZE*MAP_SIZE);
	
	var heightfield = $("#heightfield");
	heightfield[0].width = MAP_SIZE;
	heightfield[0].height = MAP_SIZE;
	
	//Have to create a frickin canvas
	var hc = $("#hc");
	hc[0].width = MAP_SIZE;
	hc[0].height = MAP_SIZE;
	var hcc = hc[0].getContext('2d');
	hcc.drawImage(heightfield[0], 0, 0, MAP_SIZE, MAP_SIZE);

	var hfdata = hcc.getImageData(0,0,MAP_SIZE, MAP_SIZE);
	//console.log(hfdata)
	for (var i = 0; i<map.length; i++){
		var x = Math.random() > 0.95 ?
			'tree' : Math.random() > 0.95 ?
				Math.random() >0.5 ? 'rock' 
				: 'tree2' 
			: 'grass';
		//console.log(hfdata.data[i*4+1]);	
		map[i] = {
			height:hfdata.data[i*4+1]/25.5,
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
			
			ctx.fillStyle = "#009900";
			if (b){
				var cb = plib.v3.normalise(plib.v3.sub(b, c));
				var cn = plib.v3.normalise(plib.v3.sub(n, c));
				var col = plib.v3.normalise(plib.v3.cross(cb, cn));
				ctx.fillStyle = "rgb(0, " + parseInt(col[0]*2550 +100) + ",0)";
			}
			ctx.beginPath();
			
			

			ctx.moveTo(n[0], n[1]);
			
			
			ctx.lineTo(c[0], c[1]);

			if(b)
				ctx.lineTo(b[0], b[1]);
			
			if(o)
				ctx.lineTo(o[0], o[1]);
			
			
			ctx.closePath();
			ctx.fill();			
			
			
			var m = $('#' + MAP[parseInt(x + y*MAP_SIZE)]['terrain'])[0];
			ctx.drawImage(
				m,
				c[0]-s/2, c[1] - s* m.height/m.width,
				s, s * m.height/m.width
				);
			//ctx.fillRect(c[0], c[1], 1, 1);	
			
		}
	
			
		
		drawHeightField(canv, point, MAP);
	});
});



