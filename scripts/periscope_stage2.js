var data = {
	complete: true
};

$('.t-head-01').each(function(i, elem) {
	var text = $(elem).text();
	if(/ship-to address/mi.test(text)) {
		var sibling = $(elem).siblings()[0];
		data.email = $(sibling).text().replace(/^.*email: |Phone:.*$/gmi, '').trim();
		data.phone = $(sibling).text().replace(/^.*Phone: /mi, '').trim();
	}
});

return data;
