/*
 * Copyright (C) 2026 RemotiveLabs
 * SPDX-License-Identifier: Apache-2.0
 */

#include "cansignals.h"

#include <QSocketNotifier>
#include <QDebug>

#include <cstring>
#include <unistd.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>

extern "C" {
#include "chassis_can.h"
#include "body_can.h"
}

CanSignals::CanSignals(const QString &chassisInterface, const QString &bodyInterface, QObject *parent) :
	QObject(parent)
{
	m_clock.start();

	m_chassisFd = openSocket(chassisInterface);
	if (m_chassisFd >= 0) {
		m_chassisNotifier = new QSocketNotifier(m_chassisFd, QSocketNotifier::Read, this);
		connect(m_chassisNotifier, &QSocketNotifier::activated, this, &CanSignals::readChassis);
	}

	m_bodyFd = openSocket(bodyInterface);
	if (m_bodyFd >= 0) {
		m_bodyNotifier = new QSocketNotifier(m_bodyFd, QSocketNotifier::Read, this);
		connect(m_bodyNotifier, &QSocketNotifier::activated, this, &CanSignals::readBody);
	}

	connect(&m_timeoutTimer, &QTimer::timeout, this, &CanSignals::checkTimeouts);
	m_timeoutTimer.start(500);

	if (m_bodyFd >= 0) {
		connect(&m_statusTimer, &QTimer::timeout, this, &CanSignals::sendStatus);
		m_statusTimer.start(kStatusCycleMs);
	}

	m_notifyTimer.setSingleShot(true);
	m_notifyTimer.setInterval(50);
	connect(&m_notifyTimer, &QTimer::timeout, this, &CanSignals::changed);
}

void CanSignals::notify()
{
	if (!m_notifyTimer.isActive())
		m_notifyTimer.start();
}

int CanSignals::openSocket(const QString &interface)
{
	int fd = socket(PF_CAN, SOCK_RAW | SOCK_NONBLOCK, CAN_RAW);
	if (fd < 0) {
		qWarning() << "Cannot create CAN socket for" << interface << ":" << strerror(errno);
		return -1;
	}

	struct ifreq ifr;
	memset(&ifr, 0, sizeof(ifr));
	strncpy(ifr.ifr_name, interface.toLocal8Bit().constData(), IFNAMSIZ - 1);
	if (ioctl(fd, SIOCGIFINDEX, &ifr) < 0) {
		qWarning() << "CAN interface" << interface << "not found:" << strerror(errno);
		close(fd);
		return -1;
	}

	struct sockaddr_can addr;
	memset(&addr, 0, sizeof(addr));
	addr.can_family = AF_CAN;
	addr.can_ifindex = ifr.ifr_ifindex;
	if (bind(fd, reinterpret_cast<struct sockaddr *>(&addr), sizeof(addr)) < 0) {
		qWarning() << "Cannot bind CAN socket to" << interface << ":" << strerror(errno);
		close(fd);
		return -1;
	}

	qInfo() << "Reading CAN frames from" << interface;
	return fd;
}

void CanSignals::update(Signal &signal, double value, State state)
{
	signal.value = value;
	signal.state = state;
	signal.seen = m_clock.elapsed();
}

void CanSignals::readChassis()
{
	struct can_frame frame;
	while (read(m_chassisFd, &frame, sizeof(frame)) == sizeof(frame)) {
		switch (frame.can_id & CAN_SFF_MASK) {
		case CHASSIS_CAN_UI_SPEED_FRAME_FRAME_ID: {
			struct chassis_can_ui_speed_frame_t msg;
			if (chassis_can_ui_speed_frame_unpack(&msg, frame.data, frame.len) != 0)
				break;
			if (chassis_can_ui_speed_frame_uispeed_is_in_range(msg.uispeed))
				update(m_speed, chassis_can_ui_speed_frame_uispeed_decode(msg.uispeed) * 3.6, Ok);
			else
				update(m_speed, 0.0, Error);
			break;
		}
		case CHASSIS_CAN_BATTERY_STATUS_FRAME_ID: {
			struct chassis_can_battery_status_t msg;
			if (chassis_can_battery_status_unpack(&msg, frame.data, frame.len) != 0)
				break;
			if (msg.state_of_charge == CHASSIS_CAN_BATTERY_STATUS_STATE_OF_CHARGE_SNA_CHOICE)
				update(m_soc, 0.0, Sna);
			else if (msg.state_of_charge == CHASSIS_CAN_BATTERY_STATUS_STATE_OF_CHARGE_ERROR_CHOICE)
				update(m_soc, 0.0, Error);
			else
				update(m_soc, chassis_can_battery_status_state_of_charge_decode(msg.state_of_charge), Ok);

			if (msg.battery_power == CHASSIS_CAN_BATTERY_STATUS_BATTERY_POWER_SNA_CHOICE)
				update(m_power, 0.0, Sna);
			else if (msg.battery_power == CHASSIS_CAN_BATTERY_STATUS_BATTERY_POWER_ERROR_CHOICE)
				update(m_power, 0.0, Error);
			else
				update(m_power, chassis_can_battery_status_battery_power_decode(msg.battery_power), Ok);
			break;
		}
		default:
			continue;
		}
		notify();
	}
}

void CanSignals::readBody()
{
	struct can_frame frame;
	while (read(m_bodyFd, &frame, sizeof(frame)) == sizeof(frame)) {
		switch (frame.can_id & CAN_SFF_MASK) {
		case BODY_CAN_GEAR_INFO_FRAME_ID: {
			struct body_can_gear_info_t msg;
			if (body_can_gear_info_unpack(&msg, frame.data, frame.len) != 0)
				break;
			update(m_gear, body_can_gear_info_gear_lever_position_decode(msg.gear_lever_position), Ok);
			break;
		}
		case BODY_CAN_TURN_LIGHT_CONTROL_FRAME_ID: {
			struct body_can_turn_light_control_t msg;
			if (body_can_turn_light_control_unpack(&msg, frame.data, frame.len) != 0)
				break;
			update(m_left, body_can_turn_light_control_left_turn_light_request_decode(msg.left_turn_light_request), Ok);
			update(m_right, body_can_turn_light_control_right_turn_light_request_decode(msg.right_turn_light_request), Ok);
			break;
		}
		default:
			continue;
		}
		notify();
	}
}

void CanSignals::sendStatus()
{
	// Report what is on the display, in the same steps the display uses
	struct body_can_dim_status_t msg;
	memset(&msg, 0, sizeof(msg));

	if (m_speed.state == Ok)
		msg.displayed_speed = body_can_dim_status_displayed_speed_encode(qRound(qBound(0.0, m_speed.value, 250.0)));
	else
		msg.displayed_speed = BODY_CAN_DIM_STATUS_DISPLAYED_SPEED_NOT_DISPLAYED_CHOICE;

	const QString g = gear();
	if (g == QLatin1String("D"))
		msg.displayed_gear = BODY_CAN_DIM_STATUS_DISPLAYED_GEAR_DRIVE_CHOICE;
	else if (g == QLatin1String("R"))
		msg.displayed_gear = BODY_CAN_DIM_STATUS_DISPLAYED_GEAR_REVERSE_CHOICE;
	else
		msg.displayed_gear = BODY_CAN_DIM_STATUS_DISPLAYED_GEAR_NOT_DISPLAYED_CHOICE;

	msg.left_indicator_lamp = leftTurn() ? BODY_CAN_DIM_STATUS_LEFT_INDICATOR_LAMP_ON_CHOICE
					     : BODY_CAN_DIM_STATUS_LEFT_INDICATOR_LAMP_OFF_CHOICE;
	msg.right_indicator_lamp = rightTurn() ? BODY_CAN_DIM_STATUS_RIGHT_INDICATOR_LAMP_ON_CHOICE
					       : BODY_CAN_DIM_STATUS_RIGHT_INDICATOR_LAMP_OFF_CHOICE;

	switch (lampState()) {
	case Error:
		msg.engine_lamp = BODY_CAN_DIM_STATUS_ENGINE_LAMP_ERROR_CHOICE;
		break;
	case Sna:
		msg.engine_lamp = BODY_CAN_DIM_STATUS_ENGINE_LAMP_SNA_CHOICE;
		break;
	default:
		msg.engine_lamp = BODY_CAN_DIM_STATUS_ENGINE_LAMP_OFF_CHOICE;
		break;
	}

	struct can_frame frame;
	memset(&frame, 0, sizeof(frame));
	frame.can_id = BODY_CAN_DIM_STATUS_FRAME_ID;
	frame.len = BODY_CAN_DIM_STATUS_LENGTH;
	if (body_can_dim_status_pack(frame.data, &msg, sizeof(frame.data)) < 0)
		return;
	if (write(m_bodyFd, &frame, sizeof(frame)) != sizeof(frame))
		qWarning() << "Cannot send DIMStatus:" << strerror(errno);
}

void CanSignals::checkTimeouts()
{
	const qint64 now = m_clock.elapsed();
	bool anyChanged = false;
	for (Signal *signal : { &m_speed, &m_power, &m_soc, &m_gear, &m_left, &m_right }) {
		if (signal->state != Missing && now - signal->seen > kTimeoutMs) {
			signal->state = Missing;
			anyChanged = true;
		}
	}
	if (anyChanged)
		notify();
}

QString CanSignals::gear() const
{
	if (m_gear.state != Ok)
		return QString();
	// GearInfo.GearLeverPosition: 0 "Reverse", 1 "Drive"
	return m_gear.value > 0.5 ? QStringLiteral("D") : QStringLiteral("R");
}

int CanSignals::lampState() const
{
	int worst = Ok;
	for (const Signal *signal : { &m_speed, &m_power, &m_soc, &m_gear, &m_left, &m_right }) {
		if (signal->state == Error)
			return Error;
		if (signal->state == Sna)
			worst = Sna;
	}
	return worst;
}
