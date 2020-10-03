var data = {
	rfps: [],
	next: !$('#body_x_grid_PagerBtnNextPage').parent()[0].classList.contains('hidden')
};

$('tr[data-object-type="rfp"]').each((i, elem) => {
	var entry = {
		origin: 'emma',
		state: 'MD',
		complete: false,
		error: false
	};

	$(elem).find('td').each((j, cell) => {
		switch (j){
			case 1:
				entry.source_id = cell.innerHTML;
				break;
			case 2:
				var link = $(cell).find('a')[0];
				entry.title = link.innerHTML;
				entry.link = link.href;
				break;
			case 4:
				entry.endDate = cell.innerHTML;
				var date = new Date(cell.innerHTML);
				if(isNaN(date.getTime())) {
					entry.parsedDate = null;
				} else {
					entry.parsedDate = date.toISOString();
				}
				break;
			case 5:
				entry.category = cell.innerHTML;
				break;
		}
	});

	data.rfps.push(entry);
});

if(data.next) $('#body_x_grid_PagerBtnNextPage').click();
return data;
