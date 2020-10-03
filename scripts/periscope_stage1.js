var headers = {},
	temp = {},
	data = { 
		rfps: [],
		next: false
	};

$('#resultsTable thead tr td').each((i, elem) => {
	elem = $(elem).text().replace(/\s/gm, '');

	if(/bid#/i.test(elem)) headers.source_id1 = i;
	if(/alternateid/i.test(elem)) headers.source_id2 = i;
	if(/description/i.test(elem)) headers.title = i;
	if(/bidopeningdate/i.test(elem)) headers.endDate = i;
});


$('#resultsTable tbody tr').each((i, elem) => {
	temp = {
		complete: false,
		error: false,
		origin: 'periscope',
		state: 'MA',
	};

	$(elem).find('td').each( function(j, cell){
		if(headers.source_id1 == j) {
			temp.source_id1 = $(cell).text().trim();
			temp.link = $(cell).find('a')[0].href.replace(/bidack/i, 'bidDetail');
		} else if (headers.title == j){
			temp.title = $(cell).text().trim();
		} else if (headers.endDate == j) {
			var date = $(cell).text().trim().split(' ')[0].trim();
			temp.endDate = date;
			temp.parsedDate = new Date(date);
		} else if(headers.source_id2 == j){
			var text = $(cell).text().trim();
			if(!!text && text.length > 0) temp.source_id2 = text;
		} 
	});

	data.rfps.push(temp);
});

if(typeof viewPage == 'function') {
	var currentpage = +document.forms[0].currentPage.value;
	data.next = $(`a[href="javascript:viewPage(${currentpage + 1})"]`).length > 0;
	if(data.next) viewPage(currentpage + 1);
}

return data;