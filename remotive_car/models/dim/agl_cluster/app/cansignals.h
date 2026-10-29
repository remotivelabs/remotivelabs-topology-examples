/*
 * Copyright (C) 2026 RemotiveLabs
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef CANSIGNALS_H
#define CANSIGNALS_H

#include <QObject>
#include <QElapsedTimer>
#include <QString>
#include <QTimer>

class QSocketNotifier;

/*
 * Vehicle signals for the cluster, read directly from the CAN buses over
 * SocketCAN and decoded with the code generated from the platform DBC files.
 *
 * Every signal carries a state next to its value, mirroring what the buses
 * express: Sna and Error are the named values the sending ECU puts on the
 * bus, Missing means no frame has been seen within the timeout.
 *
 * What the cluster displays is reported back on the body bus in the cyclic
 * DIMStatus frame, as a real cluster does, so that other ECUs and testers can
 * verify the display over CAN alone.
 */
class CanSignals : public QObject
{
	Q_OBJECT

	Q_PROPERTY(double speedKph READ speedKph NOTIFY changed)
	Q_PROPERTY(int speedState READ speedState NOTIFY changed)
	Q_PROPERTY(double motorPowerKw READ motorPowerKw NOTIFY changed)
	Q_PROPERTY(int motorPowerState READ motorPowerState NOTIFY changed)
	Q_PROPERTY(double stateOfCharge READ stateOfCharge NOTIFY changed)
	Q_PROPERTY(int stateOfChargeState READ stateOfChargeState NOTIFY changed)
	Q_PROPERTY(QString gear READ gear NOTIFY changed)
	Q_PROPERTY(int gearState READ gearState NOTIFY changed)
	Q_PROPERTY(bool leftTurn READ leftTurn NOTIFY changed)
	Q_PROPERTY(bool rightTurn READ rightTurn NOTIFY changed)
	Q_PROPERTY(int lampState READ lampState NOTIFY changed)

public:
	enum State { Ok, Missing, Sna, Error };
	Q_ENUM(State)

	explicit CanSignals(const QString &chassisInterface, const QString &bodyInterface,
			    QObject *parent = nullptr);

	double speedKph() const { return m_speed.value; }
	int speedState() const { return m_speed.state; }
	double motorPowerKw() const { return m_power.value; }
	int motorPowerState() const { return m_power.state; }
	double stateOfCharge() const { return m_soc.value; }
	int stateOfChargeState() const { return m_soc.state; }
	QString gear() const;
	int gearState() const { return m_gear.state; }
	bool leftTurn() const { return m_left.state == Ok && m_left.value > 0.5; }
	bool rightTurn() const { return m_right.state == Ok && m_right.value > 0.5; }
	// Worst state among the signals a sender reported explicitly: Error, else Sna, else Ok
	int lampState() const;

signals:
	void changed();

private:
	struct Signal {
		double value = 0.0;
		State state = Missing;
		qint64 seen = -1;
	};

	int openSocket(const QString &interface);
	void readChassis();
	void readBody();
	void sendStatus();
	void checkTimeouts();
	void update(Signal &signal, double value, State state);

	int m_chassisFd = -1;
	int m_bodyFd = -1;
	QSocketNotifier *m_chassisNotifier = nullptr;
	QSocketNotifier *m_bodyNotifier = nullptr;
	QElapsedTimer m_clock;
	QTimer m_timeoutTimer;
	QTimer m_statusTimer;
	// Frames arrive at bus rate; property change notifications are coalesced
	QTimer m_notifyTimer;
	void notify();

	Signal m_speed;
	Signal m_power;
	Signal m_soc;
	Signal m_gear;
	Signal m_left;
	Signal m_right;

	static constexpr qint64 kTimeoutMs = 3000;
	// DIMStatus cycle time, GenMsgCycleTime in body_can.dbc
	static constexpr int kStatusCycleMs = 100;
};

#endif // CANSIGNALS_H
