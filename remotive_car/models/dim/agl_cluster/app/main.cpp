/*
 * Copyright (C) 2016 The Qt Company Ltd.
 * Copyright (C) 2018,2019,2020,2022,2025 Konsulko Group
 * Copyright (C) 2026 RemotiveLabs
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Derived from the AGL cluster demo dashboard (apps/agl-cluster-demo-dashboard).
 * The KUKSA vehicle signal client is replaced by CanSignals, which reads the
 * vehicle buses directly over SocketCAN. The agl_shell integration is kept so
 * the same binary runs as the background of agl-compositor on an AGL image;
 * anywhere else it is an ordinary top-level window.
 */

#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlComponent>
#include <QQmlContext>
#include <QQuickWindow>
#include <QScreen>
#include <QTimer>
#include <QDebug>
#include QT_QPA_HEADER

#include <wayland-client.h>
#include "agl-shell-client-protocol.h"

#include "cansignals.h"

static void
global_add(void *data, struct wl_registry *reg, uint32_t name,
	   const char *interface, uint32_t version)
{
	(void) version;
	struct agl_shell **shell = static_cast<struct agl_shell **>(data);
	if (strcmp(interface, agl_shell_interface.name) == 0) {
		*shell = static_cast<struct agl_shell *>(wl_registry_bind(reg,
					name, &agl_shell_interface, 1)
		);
	}
}

static void
global_remove(void *data, struct wl_registry *reg, uint32_t id)
{
	(void) data;
	(void) reg;
	(void) id;
}

static const struct wl_registry_listener registry_listener = {
	global_add,
	global_remove,
};

static struct agl_shell *
register_agl_shell(QPlatformNativeInterface *native)
{
	struct wl_display *wl;
	struct wl_registry *registry;
	struct agl_shell *shell = nullptr;

	wl = static_cast<struct wl_display *>(native->nativeResourceForIntegration("display"));
	if (!wl)
		return nullptr;
	registry = wl_display_get_registry(wl);

	wl_registry_add_listener(registry, &registry_listener, &shell);
	wl_display_roundtrip(wl);
	wl_registry_destroy(registry);

	return shell;
}

static struct wl_surface *
getWlSurface(QPlatformNativeInterface *native, QWindow *window)
{
	void *surf = native->nativeResourceForWindow("surface", window);
	return static_cast<struct ::wl_surface *>(surf);
}

static struct wl_output *
getWlOutput(QPlatformNativeInterface *native, QScreen *screen)
{
	void *output = native->nativeResourceForScreen("output", screen);
	return static_cast<struct ::wl_output*>(output);
}

static QScreen *find_screen(const char *screen_name)
{
	QList<QScreen *> screens = qApp->screens();
	QString name(screen_name);

	for (QScreen *screen : screens) {
		if (name == screen->name())
			return screen;
	}

	return nullptr;
}

int main(int argc, char *argv[])
{
	QString myname = QString("cluster-dashboard");
	struct agl_shell *agl_shell = nullptr;

	QGuiApplication app(argc, argv);
	app.setDesktopFileName(myname);

	// agl_shell only exists on agl-compositor; on other platforms (VNC,
	// other Wayland compositors) the cluster is a plain window.
	QPlatformNativeInterface *native = nullptr;
	if (QGuiApplication::platformName() == "wayland")
		native = qApp->platformNativeInterface();
	if (native)
		agl_shell = register_agl_shell(native);
	std::shared_ptr<struct agl_shell> shell;
	if (agl_shell)
		shell.reset(agl_shell, agl_shell_destroy);
	else
		qInfo("agl_shell not available, running as a plain window");

	QScreen *screen = nullptr;
	const char *screen_name = getenv("DASHBOARD_START_SCREEN");
	if (screen_name)
		screen = find_screen(screen_name);
	if (!screen)
		screen = qApp->primaryScreen();

	CanSignals can(qEnvironmentVariable("CAN_CHASSIS", "chassiscan0"),
		       qEnvironmentVariable("CAN_BODY", "bodycan0"));

	QQmlApplicationEngine engine;
	engine.rootContext()->setContextProperty("Can", &can);

	QQmlComponent comp(&engine, QUrl("qrc:/qml/Cluster.qml"));
	QObject *obj = comp.create();
	if (!obj) {
		qCritical() << comp.errors();
		return EXIT_FAILURE;
	}
	obj->setParent(screen);
	QWindow *win = qobject_cast<QWindow *>(obj);

	if (agl_shell && win) {
		struct wl_surface *bg = getWlSurface(native, win);
		struct wl_output *output = getWlOutput(native, screen);

		// set the surface as the background
		agl_shell_set_background(agl_shell, bg, output);

		// instruct the compositor it can display after Qt has a chance
		// to load everything
		QTimer::singleShot(500, [agl_shell](){
			qDebug() << "agl_shell ready!";
			agl_shell_ready(agl_shell);
		});
	}

	return app.exec();
}
