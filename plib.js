

var plib = plib || {};


/*****************************************************************************
 * 2D Vectors 
 ****************************************************************************/
plib.v2 = plib.v2 || {};

plib.v2.add = function(p1, p2){
	return [p1[0] + p2[0], p1[1]+ p2[1]];
}
plib.v2.dot = function(r1, r2){
	return r1[0] * r2[0] + r1[1] * r2[1]
}
plib.v2.eq = function(v1, v2){
	return (v1[0]== v2[0] && v1[1] == v2[1]);
}
plib.v2.len = function(vec){
	return Math.sqrt(vec[0]*vec[0]+ vec[1]*vec[1]);
}
plib.v2.mult = function(v1, v2){
	return [v1[0] * v2[0], v1[1] * v2[1]];
}	
plib.v2.normalise = function(r){
	var len = plib.v2.len(r);
	return [r[0]/len, r[1]/len]
}
plib.v2.scale = function(p1, scale){
	return [p1[0] * scale, p1[1] * scale];
}
plib.v2.sub = function(p1, p2){
	return [p1[0] - p2[0], p1[1] - p2[1]];
}


/*****************************************************************************
 * 3D Vectors
 ****************************************************************************/
plib.v3 = plib.v3 || {};

plib.v3.add = function(p1, p2){
	return [p1[0] + p2[0], p1[1]+ p2[1], p1[2] + p2[2]];
}
plib.v3.dot = function(r1, r2){
	return r1[0] * r2[0] + r1[1] * r2[1] + r1[2] * r2[2] 
}
plib.v3.eq = function(r1, r2){
	return r1[0] == r2[0] && r1[1] == r2[1] && r1[2] == r2[2];
}
plib.v3.len = function(ray){
	return Math.sqrt(ray[0]*ray[0]+ ray[1]*ray[1] + ray[2]*ray[2]);
}
plib.v3.mult = function(p1, p2){
	return [p1[0] * p2[0], p1[1] * p2[1], p1[2] * p2[2]];
}
plib.v3.normalise = function(r){
	var len = plib.v3.len(r);
	return [r[0]/len, r[1]/len, r[2]/len]
}
plib.v3.scale = function(p1, scale){
	return [p1[0] * scale, p1[1] * scale, p1[2] * scale];
}
plib.v3.sub = function(p1, p2){
	return [p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]];
}


