SUBDIRS = po src


DISTCLEANFILES =                \
	intltool-extract        \
	intltool-merge          \
	intltool-update		\
	gnome-doc-utils.make	\
	dbr.desktop

image_DATA=	insight.png	\
	
desktopdir 	 = $(datadir)/applications
desktop_in_files = dbr.desktop.in
desktop_DATA     = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

EXTRA_DIST =                \
	dbr.spec           \
	dbr.spec.in        \
	$(desktop_in_files) \
	ChangeLog           \
	MAINTAINERS         \
	$(image_DATA)
