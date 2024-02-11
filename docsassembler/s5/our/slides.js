// S5 v1.2a1 slides.js -- released into the Public Domain
//
// Please see http://www.meyerweb.com/eric/tools/s5/credits.html for information
// about all the wonderful and talented contributors to this code!

// Tuned by Vitaliy Filippov (http://wiki.4intra.net/)
// 1) Per-slide scaling mode, activated by setting window.s5ScaleEachSlide = true;
// 2) Save/restore of current position in cookies (upon "Reload" clicks),
//    activated by setting window.slideshowId = <string>;

// Adapter for Pandoc by Stas Fomin (http://wiki.4intra.net/)

var undef;
var slideCSS = '';
var snum = 0;
var smax = 1;
var incpos = 0;
var number = undef;
var s5mode = true;
var defaultView = 'slideshow';
var controlVis = 'visible';

var previousSlide = 0;
var presentationStart = new Date();
var slideStart = new Date();
var s5ScaleEachSlide = true;

var countdown = {
	timer: 0,
	state: 'pause',
	start: new Date(),
	end: 0,
	remaining: 0
};

var isIE = navigator.appName == 'Microsoft Internet Explorer' && navigator.userAgent.indexOf('Opera') < 1 ? 1 : 0;
var isOp = navigator.userAgent.indexOf('Opera') > -1 ? 1 : 0;


function hasClass(object, className) {
	if (!object.className) return false;
	return (object.className.search('(^|\\s)' + className + '(\\s|$)') != -1);
}

function hasValue(object, value) {
	if (!object) return false;
	return (object.search('(^|\\s)' + value + '(\\s|$)') != -1);
}

function removeClass(object,className) {
	if (!object || !hasClass(object,className)) return;
	object.className = object.className.replace(new RegExp('(^|\\s)'+className+'(\\s|$)'), RegExp.$1+RegExp.$2);
}

function addClass(object,className) {
	if (!object || hasClass(object, className)) return;
	if (object.className) {
		object.className += ' '+className;
	} else {
		object.className = className;
	}
}

function GetElementsWithClassName(elementName,className) {
	var allElements = document.getElementsByTagName(elementName);
	var elemColl = new Array();
	for (var i = 0; i< allElements.length; i++) {
		if (hasClass(allElements[i], className)) {
			elemColl[elemColl.length] = allElements[i];
		}
	}
	return elemColl;
}

function isParentOrSelf(element, id) {
	if (element == null || element.nodeName=='BODY') return false;
	else if (element.id == id || element.nodeName.toLowerCase() == id) return true;
	else return isParentOrSelf(element.parentNode, id);
}

function nodeValue(node) {
	var result = "";
	if (node.nodeType == 1) {
		var children = node.childNodes;
		for (var i = 0; i < children.length; ++i) {
			result += nodeValue(children[i]);
		}		
	}
	else if (node.nodeType == 3) {
		result = node.nodeValue;
	}
	return(result);
}

function slideLabel() {
	var slideColl = GetElementsWithClassName('*','slide');
	var list = document.getElementById('jumplist');
	smax = slideColl.length;
	for (var n = 0; n < smax; n++) {
		var obj = slideColl[n];

		var did = 'slide' + n.toString();
		obj.setAttribute('id',did);

//		if (isOp) continue;  // Opera fix (hallvord)

		if (!list) continue; // for print view

		var otext = '';
		var menu = obj.firstChild;
		if (!menu) continue; // to cope with empty slides
		while (menu && menu.nodeType == 3) {
			menu = menu.nextSibling;
		}
		if (!menu) continue; // to cope with slides with only text nodes

		var menunodes = menu.childNodes;
		for (var o = 0; o < menunodes.length; o++) {
			otext += nodeValue(menunodes[o]);
		}
		list.options[list.length] = new Option(n + ' : '  + otext, n);
	}
}

function currentSlide() {
	var cs;
	if (document.getElementById) {
		cs = document.getElementById('currentSlide');
	} else {
		cs = document.currentSlide;
	}
	cs.innerHTML = '<a id="plink" href="">' +
		'<span id="csHere">' + snum + '<\/span> ' +
		'<span id="csSep">\/<\/span> ' +
		'<span id="csTotal">' + (smax-1) + '<\/span>' +
		'<\/a>'
		;
	if (snum == 0) {
		cs.style.visibility = 'hidden';
	} else {
		cs.style.visibility = 'visible';
	}
}

function go(step, force) {
	if (document.getElementById('slideProj').childNodes[1].disabled || step == 0 && !force) return;
	if (s5ScaleEachSlide) {
		setFontSize('body', '24px');
		initialFontSize = 24;
	}
	var jl = document.getElementById('jumplist');
	var cid = 'slide' + snum;
	var ce = document.getElementById(cid);
	if (incrementals[snum].length > 0) {
		for (var i = 0; i < incrementals[snum].length; i++) {
			removeClass(incrementals[snum][i], 'previous');
			removeClass(incrementals[snum][i], 'current');
			removeClass(incrementals[snum][i], 'incremental');
		}
	}
	if (step != 'j') {
		snum += step;
		lmax = smax - 1;
		if (snum > lmax) snum = lmax;
		if (snum < 0) snum = 0;
	} else {
		snum = parseInt(jl.value);
	}
	if (step < 0) {incpos = incrementals[snum].length} else {incpos = 1}
	if (incrementals[snum].length > 0) {
		for (var i = 0; i < incrementals[snum].length && i < incpos-1; i++) {
			addClass(incrementals[snum][i], 'previous');
			removeClass(incrementals[snum][i], 'current');
			removeClass(incrementals[snum][i], 'incremental');
		}
		removeClass(incrementals[snum][incpos-1], 'previous');
		addClass(incrementals[snum][incpos-1], 'current');
		removeClass(incrementals[snum][incpos-1], 'incremental');
		for (var i = incpos; i < incrementals[snum].length; i++) {
			removeClass(incrementals[snum][i], 'previous');
			removeClass(incrementals[snum][i], 'current');
			addClass(incrementals[snum][i], 'incremental');
		}
	}
	if (s5ScaleEachSlide) {
		fontScale(); // Slide font and/or content scaling
	}
	var nid = 'slide' + snum;
	var ne = document.getElementById(nid);
	if (!ne) {
		ne = document.getElementById('slide0');
		snum = 0;
	}
	if (isOp) { //hallvord
		location.hash = nid;
		window.scrollTo(0);
	} else {
		removeClass(ce, 'visible');
		addClass(ne, 'visible');
	} //hallvord
	jl.selectedIndex = snum;
	setS5Cookie(snum);
	currentSlide();
	permaLink();
	setBodyClass();
	number = undef;
}

function goTo(target) {
	if (target >= smax || target == snum) return;
	go(target - snum);
}

function subgo(step) {
	if (step > 0) {
		removeClass(incrementals[snum][incpos - 1],'current');
		addClass(incrementals[snum][incpos - 1],'previous');
		removeClass(incrementals[snum][incpos], 'incremental');
		addClass(incrementals[snum][incpos],'current');
		incpos++;
	} else {
		incpos--;
		removeClass(incrementals[snum][incpos],'current');
		addClass(incrementals[snum][incpos], 'incremental');
		removeClass(incrementals[snum][incpos - 1],'previous');
		addClass(incrementals[snum][incpos - 1],'current');
	}
	loadNote();
}

function toggle() {
	var slideColl = GetElementsWithClassName('*','slide');
	var slides = document.getElementById('slideProj').childNodes[1];
	var outline = document.getElementById('outlineStyle').childNodes[1];
	if (!slides.disabled) {
		slides.disabled = true;
		s5mode = false;
		setFontSize('body', '1em');
		for (var n = 0; n < smax; n++) {
			var slide = slideColl[n];
			addClass(slide, 'visible');
		}
		outline.disabled = false;
		setFontSize('body', '1em');
	} else {
		slides.disabled = false;
		outline.disabled = true;
		s5mode = true;
		fontScale();
		for (var n = 0; n < smax; n++) {
			var slide = slideColl[n];
			removeClass(slide, 'visible');
		}
		addClass(slideColl[snum], 'visible');
	}
}

function showHide(action) {
	var obj = GetElementsWithClassName('*','hideme')[0];
	switch (action) {
	case 's': obj.style.visibility = 'visible'; break;
	case 'h': obj.style.visibility = 'hidden'; break;
	case 'k':
		if (obj.style.visibility != 'visible') {
			obj.style.visibility = 'visible';
		} else {
			obj.style.visibility = 'hidden';
		}
	break;
	}
}

// 'keys' code adapted from MozPoint (http://mozpoint.mozdev.org/)
function keys(key) {
	if (!key) {
		key = event;
		key.which = key.keyCode;
	}
	if (key.which == 84) {
		toggle();
		return;
	}
	if (s5mode) {
		switch (key.which) {
			case 10: // return
			case 13: // enter
				if (window.event && isParentOrSelf(window.event.srcElement, 'controls')) return;
				if (key.target && isParentOrSelf(key.target, 'controls')) return;
				if(number != undef) {
					goTo(number);
					break;
				}
			case 32: // spacebar
			case 34: // page down
			case 39: // rightkey
			case 40: // downkey
				if(number != undef) {
					go(number);
				} else if (!incrementals[snum] || incpos >= incrementals[snum].length) {
					go(1);
				} else {
					subgo(1);
				}
				break;
			case 33: // page up
			case 37: // leftkey
			case 38: // upkey
				if(number != undef) {
					go(-1 * number);
				} else if (!incrementals[snum] || incpos <= 1) {
					go(-1);
				} else {
					subgo(-1);
				}
				break;
			case 36: // home
				goTo(0);
				break;
			case 35: // end
				goTo(smax-1);
				break;
			case 67: // c
				showHide('k');
				break;
		}
		if (key.which < 48 || key.which > 57) {
			number = undef;
		} else {
			if (window.event && isParentOrSelf(window.event.srcElement, 'controls')) return;
			if (key.target && isParentOrSelf(key.target, 'controls')) return;
			number = (((number != undef) ? number : 0) * 10) + (key.which - 48);
		}
	}
	return false;
}

function clicker(e) {
	number = undef;
	var target;
	if (window.event) {
		target = window.event.srcElement;
		e = window.event;
	} else target = e.target;
	if (target.href != null || hasValue(target.rel, 'external') || isParentOrSelf(target, 'controls') || isParentOrSelf(target,'embed') || isParentOrSelf(target,'object')) return true;
	if (!e.which || e.which == 1) {
		if (!incrementals[snum] || incpos >= incrementals[snum].length) {
			go(1);
		} else {
			subgo(1);
		}
	}
}

function findSlide(hash) {
	var target = null;
	var slides = GetElementsWithClassName('*','slide');
	for (var i = 0; i < slides.length; i++) {
		var targetSlide = slides[i];
		if ( (targetSlide.name && targetSlide.name == hash)
		 || (targetSlide.id && targetSlide.id == hash) ) {
			target = targetSlide;
			break;
		}
	}
	while(target != null && target.nodeName != 'BODY') {
		if (hasClass(target, 'slide')) {
			return parseInt(target.id.slice(5));
		}
		target = target.parentNode;
	}
	return null;
}

function setBodyClass() {
	document.body.className = document.body.className.replace(/\s+active\d+/, '')+' active'+snum;
}

function slideJump() {
	if (window.location.hash == null) return;
	var sregex = /^#slide(\d+)$/;
	var matches = sregex.exec(window.location.hash);
	var dest = null;
	if (matches != null) {
		dest = parseInt(matches[1]);
	} else {
		dest = findSlide(window.location.hash.slice(1));
	}
	if (dest == null) {
		dest = getS5Cookie();
	}
	dest = dest || 0;
	go(dest - snum, true);
}

function fixLinks() {
	var thisUri = window.location.href;
	thisUri = thisUri.slice(0, thisUri.length - window.location.hash.length);
	var aelements = document.getElementsByTagName('A');
	for (var i = 0; i < aelements.length; i++) {
		var a = aelements[i].href;
		var slideID = a.match('\#slide[0-9]{1,2}');
		if ((slideID) && (slideID[0].slice(0,1) == '#')) {
			var dest = findSlide(slideID[0].slice(1));
			if (dest != null) {
				if (aelements[i].addEventListener) {
					aelements[i].addEventListener("click", new Function("e",
						"if (document.getElementById('slideProj').childNodes[1].disabled) return;" +
						"go("+dest+" - snum); " +
						"if (e.preventDefault) e.preventDefault();"), true);
				} else if (aelements[i].attachEvent) {
					aelements[i].attachEvent("onclick", new Function("",
						"if (document.getElementById('slideProj').childNodes[1].disabled) return;" +
						"go("+dest+" - snum); " +
						"event.returnValue = false;"));
				}
			}
		}
	}
}

function externalLinks() {
	if (!document.getElementsByTagName) return;
	var anchors = document.getElementsByTagName('a');
	for (var i=0; i<anchors.length; i++) {
		var anchor = anchors[i];
		if (anchor.getAttribute('href') && hasValue(anchor.rel, 'external')) {
			anchor.target = '_blank';
			addClass(anchor,'external');
		}
	}
}

function permaLink() {
	document.getElementById('plink').href = window.location.pathname + '#slide' + snum;
}

function createControls() {
	var controlsDiv = document.getElementById("controls");
	if (!controlsDiv) return;
	var hider = ' onmouseover="showHide(\'s\');" onmouseout="showHide(\'h\');"';
	var hideDiv, hideList = '';
	if (controlVis == 'hidden') {
		hideDiv = hider;
	} else {
		hideList = hider;
	}
	controlsDiv.innerHTML = '<form action="#" id="controlForm"' + hideDiv + '>' +
	'<div id="navLinks">' +
	'<a id="print" href="javascript:openPrintView();" title="Print">&#9113;<\/a>' +
	'<a accesskey="t" id="toggle" href="javascript:toggle();">&#216;<\/a>' +
	'<a accesskey="z" id="prev" href="javascript:go(-1);">&laquo;<\/a>' +
	'<a accesskey="x" id="next" href="javascript:go(1);">&raquo;<\/a>' +
	'<div id="navList"' + hideList + '><select id="jumplist" onchange="go(\'j\');"><\/select><\/div>' +
	'<\/div><\/form>';
	if (controlVis == 'hidden') {
		var hidden = document.getElementById('navLinks');
	} else {
		var hidden = document.getElementById('jumplist');
	}
	addClass(hidden, 'hideme');
}

// "fontScale" name resides from history
// really it supports content scaling by now
var initialFontSize = 24;
function fontScale()
{
	if (!s5mode) return false;
	if (window.innerHeight) {
		var vSize = window.innerHeight;
		var hSize = window.innerWidth;
	} else if (document.documentElement.clientHeight) {
		var vSize = document.documentElement.clientHeight;
		var hSize = document.documentElement.clientWidth;
	} else if (document.body.clientHeight) {
		var vSize = document.body.clientHeight;
		var hSize = document.body.clientWidth;
	} else {
		var vSize = 700;  // assuming 1024x768, minus chrome and such
		var hSize = 1024; // these do not account for kiosk mode or Opera Show
	}
	vSize -= 32;
	var newSize;
	if (!s5ScaleEachSlide)
	{
		var vScale = 32;  // both yield 24 at 1024x768
		var hScale = 42;  // perhaps should auto-calculate based on theme's declared value?
		newSize = Math.min(Math.round(vSize/vScale),Math.round(hSize/hScale));
		setFontSize('body', newSize + 'px');
		initialFontSize = newSize;
		reflowHack();
	}
	else
		contentScale(document.getElementById('slide'+snum), hSize, vSize, initialFontSize);
}


function getIncrementals(obj, inclen) {
	var incrementals = new Array();
	if (!obj)
		return incrementals;
	if (!inclen)
		inclen = 0;
	var children = obj.childNodes;
	for (var i = 0; i < children.length; i++)
	{
		var child = children[i];
		if (hasClass(child, 'anim'))
		{
			for (var j = 0; j < child.childNodes.length; j++)
				if (child.childNodes[j].nodeType == 1)
					addClass(child.childNodes[j], 'incremental');
		}
		else if (hasClass(child, 'incremental'))
		{
			incrementals[incrementals.length] = child;
			removeClass(child,'incremental');
		}
		incrementals = incrementals.concat(getIncrementals(child, incrementals.length));
	}
	return incrementals;
}

function createIncrementals() {
	var incrementals = new Array();
	for (var i = 0; i < smax; i++) {
		incrementals[i] = getIncrementals(document.getElementById('slide'+i));
	}
	return incrementals;
}

function defaultCheck() {
	var allMetas = document.getElementsByTagName('meta');
	for (var i = 0; i< allMetas.length; i++) {
		if (allMetas[i].name == 'defaultView') {
			defaultView = allMetas[i].content;
		}
		if (allMetas[i].name == 'controlVis') {
			controlVis = allMetas[i].content;
		}
	}
}

// Key trap fix, new function body for trap()
function trap(e) {
	if (!e) {
		e = event;
		e.which = e.keyCode;
	}
	try {
		modifierKey = e.ctrlKey || e.altKey || e.metaKey;
	}
	catch(e) {
		modifierKey = false;
	}
	return modifierKey || e.which == 0;
}

function resetElapsedTime() {
	presentationStart = new Date();
	slideStart = new Date();
	updateElaspedTime();
}

function resetElapsedSlide() {
	if (snum != previousSlide) {
		slideStart = new Date();
		previousSlide = snum;
		updateElaspedTime();
	}
}

function windowChange() {
	fontScale();
}

function getCookie(name)
{
	var cookie = " " + document.cookie;
	var search = " " + name + "=";
	var setStr = null;
	var offset = 0;
	var end = 0;
	if (cookie.length > 0) {
		offset = cookie.indexOf(search);
		if (offset != -1) {
			offset += search.length;
			end = cookie.indexOf(";", offset)
			if (end == -1) {
				end = cookie.length;
			}
			setStr = unescape(cookie.substring(offset, end));
		}
	}
	return setStr;
}

function setS5Cookie(snum)
{
	var a = [], c = getCookie('s5slide');
	if (c)
		a = c.split(',');
	var i;
	var sid = window.slideshowId;
	if (!sid)
		sid = 0;
	sid = ''+sid;
	for (i = 0; i < a.length; i++)
	{
		c = a[i].split(':');
		if (c.length < 2)
			a[i] = '';
		else if (c[0] == sid)
		{
			a[i] = sid+':'+snum;
			break;
		}
	}
	if (i >= a.length || !a.length)
		a.push(sid+':'+snum);
	document.cookie='s5slide='+escape(a.join(','))+'; path=/';
}

function getS5Cookie()
{
	var a, c;
	var sid = window.slideshowId;
	if (!sid)
		sid = 0;
	sid = ''+sid;
	if (c = getCookie('s5slide'))
	{
		var a = c.split(',');
		for (var i = 0; i < a.length; i++)
		{
			c = a[i].split(':');
			if (c[0] == sid)
				return parseInt(c[1]);
		}
	}
	return null;
}

function startup()
{
	defaultCheck();
	if (defaultView == 'print')
	{
		slideLabel();
		incrementals = createIncrementals();
		printView();
	}
	else
	{
		createControls(); // hallvord
		slideLabel();
		incrementals = createIncrementals();
		fixLinks();
		externalLinks();
		slideJump();
		fontScale();
		if (defaultView == 'outline')
		{
			toggle();
		}
		document.onkeyup = keys;
		document.onkeypress = trap;
		document.onclick = clicker;
		window.onresize = function(){setTimeout('windowChange()',5);}
	}
}

function openPrintView()
{
	var pageSize = prompt("Enter page size in mm for printing (A4 = 297x210)", '297x210');
	if (pageSize)
	{
		window.location.href = window.location.href.replace(/#.*$/, '') + '&print=' + encodeURIComponent(pageSize);
	}
}

function printView()
{
	var ce, sl, wrap, lay;
	var header = document.getElementsByClassName('header')[0];
	var footer = document.getElementsByClassName('footer')[0];
	for (sl = 0; ce = document.getElementById('slide'+sl); sl++)
	{
		wrap = document.createElement('div');
		wrap.className = 'body';
		if (incrementals[sl].length > 0)
		{
			for (var i = 0; i < incrementals[sl].length-1; i++)
			{
				addClass(incrementals[sl][i], 'previous');
				removeClass(incrementals[sl][i], 'current');
				removeClass(incrementals[sl][i], 'incremental');
			}
		}
		if (s5ScaleEachSlide)
		{
			contentScale(ce, s5PrintPageSize[0], s5PrintPageSize[1], initialFontSize);
			wrap.style.fontSize = ce._lastFontSize+'px';
		}
		ce.parentNode.insertBefore(wrap, ce);
		lay = document.createElement('div');
		lay.className = 'layout';
		lay.appendChild(header.cloneNode(true));
		lay.appendChild(footer.cloneNode(true));
		wrap.appendChild(lay);
		wrap.appendChild(ce);
	}
	document.body.className = '';
	header = document.getElementsByClassName('layout')[0];
	header.parentNode.removeChild(header);
}

window.onload = startup;


