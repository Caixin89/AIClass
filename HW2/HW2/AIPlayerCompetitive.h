#pragma once
#include <vector>
#include <tuple>
#include <string>
#include <sstream>
#include <stack>
#include <limits>
#include <chrono>
//#include <iostream>
#include <unordered_map>
//#include <unordered_set>
//#include <algorithm>

typedef unsigned char BYTE;

using namespace std;
using namespace chrono;

class AIPlayerCompetitive
{
private:
	string GetTilePosInStr(BYTE aX, BYTE aY)
	{
		stringstream ss;
		ss << (char)('A' + aX);
		ss << (aY + 1);
		return ss.str();
	}

	char GetOppositeSymbol(char aMySymbol)
	{
		return aMySymbol == 'X' ? 'O' : 'X';
	}

	vector<tuple<BYTE, BYTE, string>> Actions(char aMySymbol)
	{
		vector<tuple<BYTE, BYTE, string>> actions;
		//consider all raid moves
		for (BYTE i = 0; i < dimension; ++i)
			for (BYTE j = 0; j < dimension; ++j)
			{
				//if unoccupied:
				if (board[i][j] == '.')
				{
					string moveType = "";
					char otherSymbol = GetOppositeSymbol(aMySymbol);
					//if adjacent to a friendly tile and adjacent to 
					//multiple enemy tiles, try raid
					if ((j > 0 && board[i][j - 1] == aMySymbol) ||
						(j < dimension - 1 && board[i][j + 1] == aMySymbol) ||
						(i > 0 && board[i - 1][j] == aMySymbol) ||
						(i < dimension - 1 && board[i + 1][j] == aMySymbol))
						if ((j > 0 && board[i][j - 1] == otherSymbol) ||
							(j < dimension - 1 && board[i][j + 1] == otherSymbol) ||
							(i > 0 && board[i - 1][j] == otherSymbol) ||
							(i < dimension - 1 && board[i + 1][j] == otherSymbol))
						{
							moveType = "Raid";
							actions.push_back(tuple<BYTE, BYTE, string>(j, i, moveType));
						}
				}
			}
		//consider all stake moves
		for (BYTE i = 0; i < dimension; ++i)
			for (BYTE j = 0; j < dimension; ++j)
			{
				//if unoccupied:
				if (board[i][j] == '.')
				{
					string moveType = "Stake";
					actions.push_back(tuple<BYTE, BYTE, string>(j, i, moveType));
				}
			}
		return actions;
	}

	void EnterState(tuple<BYTE, BYTE, string> & aAction, char aMySymbol)
	{
		BYTE x = get<0>(aAction);
		BYTE y = get<1>(aAction);
		vector<tuple<BYTE, BYTE, char>> affectedTiles;
		affectedTiles.push_back(tuple<int, int, char>(x, y, '.'));
		int additionalUtility = cellValues[y][x];
		board[y][x] = aMySymbol;
		if (get<2>(aAction) == "Raid")
		{
			char otherSymbol = GetOppositeSymbol(aMySymbol);
			if (x > 0 && board[y][x - 1] == otherSymbol)
			{
				affectedTiles.push_back(tuple<BYTE, BYTE, char>(x - 1, y, otherSymbol));
				board[y][x - 1] = aMySymbol;
				additionalUtility += cellValues[y][x - 1] * 2;
			}
			if (x < dimension - 1 && board[y][x + 1] == otherSymbol)
			{
				affectedTiles.push_back(tuple<BYTE, BYTE, char>(x + 1, y, otherSymbol));
				board[y][x + 1] = aMySymbol;
				additionalUtility += cellValues[y][x + 1] * 2;
			}
			if (y > 0 && board[y - 1][x] == otherSymbol)
			{
				affectedTiles.push_back(tuple<BYTE, BYTE, char>(x, y - 1, otherSymbol));
				board[y - 1][x] = aMySymbol;
				additionalUtility += cellValues[y - 1][x] * 2;
			}
			if (y < dimension - 1 && board[y + 1][x] == otherSymbol)
			{
				affectedTiles.push_back(tuple<BYTE, BYTE, char>(x, y + 1, otherSymbol));
				board[y + 1][x] = aMySymbol;
				additionalUtility += cellValues[y + 1][x] * 2;
			}
		}
		undoStack.push(tuple<vector<tuple<BYTE, BYTE, char>>, int>(affectedTiles, currUtility));
		if (aMySymbol == youPlay)
			currUtility += additionalUtility;
		else
			currUtility -= additionalUtility;
	}

	void UndoState()
	{
		vector<tuple<BYTE, BYTE, char>> affectedTiles = get<0>(undoStack.top());
		int oldUtility = get<1>(undoStack.top());
		undoStack.pop();
		for (auto &tile : affectedTiles)
			board[get<1>(tile)][get<0>(tile)] = get<2>(tile);
		currUtility = oldUtility;
	}

	int ComputeUtility()
	{
		int score = 0;
		char enemySymbol = GetOppositeSymbol(youPlay);
		for (BYTE i = 0; i < dimension; ++i)
			for (BYTE j = 0; j < dimension; ++j)
				if (board[i][j] == youPlay)
					score += cellValues[i][j];
				else if (board[i][j] == enemySymbol)
					score -= cellValues[i][j];
		return score;
	}

	int Min_Value(BYTE aDepth, int aAlpha, int aBeta)
	{
		duration<double> time_span = duration_cast<duration<double>>(high_resolution_clock::now() - startTime);
		if (maxDepth > 1 && time_span.count() > moveDuration)
		{
			exitNow = true;
			return -1;
		}
		if (numOfUnoccupiedTiles == aDepth)
		{
			reachedTerminal = true;
			return currUtility;
		}
		if (aDepth == maxDepth)
			return currUtility;
		char enemySymbol = GetOppositeSymbol(youPlay);
		vector<tuple<BYTE, BYTE, string>> actions = Actions(enemySymbol);
		int smallestVal = numeric_limits<int>::max();
		for (int i = 0; i < actions.size(); ++i)
		{
			tuple<BYTE, BYTE, string> action = actions[i];
			EnterState(action, enemySymbol);
			int val = Max_Value(aDepth + 1, aAlpha, aBeta);
			if (exitNow)
				return -1;
			UndoState();
			if (val < smallestVal)
			{
				smallestVal = val;
			}
			if (smallestVal <= aAlpha)
				break;
			aBeta = smallestVal < aBeta ? smallestVal : aBeta;
		}
		return smallestVal;
	}

	int Max_Value(BYTE aDepth, int aAlpha, int aBeta)
	{
		duration<double> time_span = duration_cast<duration<double>>(high_resolution_clock::now() - startTime);
		if (maxDepth > 1 && time_span.count() > moveDuration)
		{
			exitNow = true;
			return -1;
		}
		if (numOfUnoccupiedTiles == aDepth)
		{
			reachedTerminal = true;
			return currUtility; //return utility value
		}
		if (aDepth == maxDepth)
			return currUtility; //return eval value
		vector<tuple<BYTE, BYTE, string>> actions = Actions(youPlay);
		int largestVal = numeric_limits<int>::min();
		for (int i = 0; i < actions.size(); ++i)
		{
			tuple<BYTE, BYTE, string> action = actions[i];
			EnterState(action, youPlay);
			int val = Min_Value(aDepth + 1, aAlpha, aBeta);
			if (exitNow)
				return -1;
			UndoState();
			if (val > largestVal)
			{
				//bestMoveIdx = i;
				largestVal = val;
			}
			if (largestVal >= aBeta)
				break;
			aAlpha = largestVal > aAlpha ? largestVal : aAlpha;
		}
		return largestVal;
	}

	tuple<string, string, string> AlphaBeta()
	{
		int largestVal = numeric_limits<int>::min();
		int alpha = numeric_limits<int>::min();
		int beta = numeric_limits<int>::max();
		vector<tuple<BYTE, BYTE, string>> actions = Actions(youPlay);
		tuple<BYTE, BYTE, string> bestAction;
		for (int i = 0; i < actions.size(); ++i)
		{
			tuple<BYTE, BYTE, string> action = actions[i];
			EnterState(action, youPlay);
			int val = Min_Value(1, alpha, beta);
			if (exitNow)
				return tuple<string, string, string>();
			UndoState();
			if (val > largestVal)
			{
				largestVal = val;
				bestAction = action;
			}
			alpha = largestVal > alpha ? largestVal : alpha;
		}
		EnterState(bestAction, youPlay);
		string boardStr = DumpBoardToStr();
		UndoState();
		string move = GetTilePosInStr(get<0>(bestAction), get<1>(bestAction));
		string moveType = get<2>(bestAction);
		return tuple<string, string, string>(move, moveType, boardStr);
	}

	string DumpBoardToStr()
	{
		stringstream ss;
		for (BYTE i = 0; i < dimension; ++i)
		{
			for (BYTE j = 0; j < dimension; ++j)
				ss << board[i][j];
			if (i < dimension - 1)
				ss << '\n';
		}
		return ss.str();
	}

	int NumberOfUnoccupiedTiles()
	{
		int count = 0;
		for (int i = 0; i < dimension; ++i)
			for (int j = 0; j < dimension; ++j)
				if (board[i][j] == '.')
					++count;
		return count;
	}

	void CalculateMaxMoveTime()
	{
		moveDuration = double(timeLeft) / numOfUnoccupiedTiles - 0.01;
	}

public:
	AIPlayerCompetitive(BYTE aDimension, string aMode, char aYouPlay, BYTE aMaxDepth, double aTimeLeft, vector<vector<char>> &aBoard, vector<vector<int>> &aCellValues)
		: dimension(aDimension), mode(aMode), youPlay(aYouPlay), maxDepth(1), timeLeft(aTimeLeft), board(aBoard), cellValues(aCellValues), exitNow(false), reachedTerminal(false)
	{
		numOfUnoccupiedTiles = NumberOfUnoccupiedTiles();
		currUtility = ComputeUtility();
		CalculateMaxMoveTime();
	}

	tuple<string, string, string> Solve()
	{
		startTime = high_resolution_clock::now();
		tuple<string, string, string> result, tmp;
		while (true)
		{
			//cout << "Depth " << (int)maxDepth << endl;
			tmp = AlphaBeta();
			if (exitNow)
				break;
			result = tmp;
			if (reachedTerminal)
			{
				//cout << "Completed the whole tree!" << endl;
				break;
			}
			++maxDepth;
		}
		//cout << "Reached depth " << (int)maxDepth << endl;
		return result;
	}

private:
	stack<tuple<vector<tuple<BYTE, BYTE, char>>, int>> undoStack;
	vector<vector<int>>& cellValues;
	vector<vector<char>>& board;
	BYTE dimension;
	string mode;
	BYTE maxDepth;
	double timeLeft;
	char youPlay;
	high_resolution_clock::time_point startTime;
	bool exitNow, reachedTerminal;
	double moveDuration;
	static const double totalGameTime;
	int numOfUnoccupiedTiles;
	int currUtility;
};

#pragma once
