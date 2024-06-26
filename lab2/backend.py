import json

import numpy as np
from bezier import Curve
from numpy import linalg

import algorithms
import missile


def unitVector(v):
    return v / linalg.norm(v)


def orthogonalVector(v):
    return np.array([-v[1], v[0]])


class TrajectoryGenerator:
    def __init__(self, request_s):
        self._request = json.loads(request_s)
        self._response = {}

        self._stepsCount = self._request['StepsCount']
        self._aircraftTrajectory = None

        # Генерация траектории ЛА
        curvesBasisPoints = np.hstack(tuple(map(requestPointToNPPoint,
                                                self._request['AircraftPoints'])))
        at = calculateAircraftTrajectory(curvesBasisPoints, self._stepsCount)
        self._response = {'AircraftTrajectory'
                          : list(map(npPointToResponsePoint,
                                     np.hsplit(at, np.shape(at)[1])))}
        self._aircraftTrajectory = at

        # Задание параметров ракет
        settings = self._request['Missiles']
        usual = missile.Missile()
        usual.stepsCount = self._stepsCount
        usual.launchPoint = requestPointToNPPoint(settings['LaunchPoint'])
        direction = requestPointToNPPoint(settings['Direction']) - usual.launchPoint
        usual.startVelocity = unitVector(direction) * settings['VelocityModule']
        usual.controller = algorithms.Proportional(settings['PropCoeff'])

        fuzzy = usual.copy()
        fuzzy.controller = algorithms.Fuzzy(settings['Inference'],
                                             settings['Defuzzification'])
        # Генерация траектории ракеты с пропорциональным методом наведением
        ut = usual.trajectory(self._aircraftTrajectory)
        ut = list(map(npPointToResponsePoint, np.hsplit(ut, np.shape(ut)[1])))
        self._response['UsualMissile'] = {'Trajectory': ut, 'IsHit': usual.hasHit}
        # Генерация траектории ракеты с нечеткой модификацией пропорционального метода наведения
        ft = fuzzy.trajectory(self._aircraftTrajectory)
        ft = list(map(npPointToResponsePoint, np.hsplit(ft, np.shape(ft)[1])))
        self._response['FuzzyMissile'] = {'Trajectory': ft, 'IsHit': fuzzy.hasHit}

        self.response_s = json.dumps(self._response)


def calculateAircraftTrajectory(curvesBasisPoints, stepsCount):
    curves = npPointsToCurves(curvesBasisPoints, 3)

    evaluate = lambda curve: \
        curve.evaluate_multi(np.linspace(0.0, 1.0, stepsCount // len(curves)))

    t = np.hstack(tuple(map(evaluate, curves)))
    print(t)
    return t


def requestPointToNPPoint(p):
    return np.array([[p['x']], [p['y']]], np.float64)


def npPointToResponsePoint(p):
    return {'x': p[0, 0], 'y': p[1, 0]}


def npPointsToCurves(curvesBasisPoints, maxPerCurvePointsCount):
    if curvesBasisPoints.size == 0:
        return []
    print(curvesBasisPoints)
    result = [Curve.from_nodes(curvesBasisPoints[:, :maxPerCurvePointsCount])]
    result.extend(npPointsToCurves(curvesBasisPoints[:, maxPerCurvePointsCount - 1:],
                                   maxPerCurvePointsCount))
    print(result)
    return result
