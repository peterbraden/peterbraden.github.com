var sys = require("sys"),
	http = require("http"),
	url = require("url");

http.createServer(function (request, response) {
	var params = url.parse(request.url, true);
	if (params.query){
		var page = http.createClient(80, params.query.url);
		var request = page.request("GET", "/", {"host": params.query.url});
		
		response.writeHead(200, {"Content-Type": "text/html"});
		var cont = "", stat, header;

		request.addListener('response', function (resp) {
			stat = resp.statusCode;
			header = JSON.stringify(resp.headers);

			resp.setBodyEncoding("utf8");
			resp.addListener("data", function (chunk) {
				cont +=chunk
			});
			resp.addListener('end', function(){
				response.write("<h1>PROXY: " + params.query.url + " </h1><h2>" + stat + "</h2>" + header + "</hr />");
				response.write(cont);
				response.close()
			});
		});
		request.close();
	}else{
		response.writeHead(200, {"Content-Type": "text/html"});
		response.write("<h1>Proxy</h1><form action='.'><input type='text' name='url' value='URL'></input");
		response.close();
	}
	}).listen(8000);
sys.puts("Server running at http://127.0.0.1:8000/");
