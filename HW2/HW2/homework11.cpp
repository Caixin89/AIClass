#include "AIPlayer.h"
#include "AIPlayerCompetitive.h"
//#include "AIPlayerCompetitive2.h"
#include <fstream>

void LoadBoardFromFile(ifstream & aFileHandle, vector<vector<char>> &aBoard, vector<vector<int>> &aCellValues)
{
	string line;
	for (BYTE i = 0; i < aBoard.size(); ++i)
	{
		getline(aFileHandle, line);
		stringstream linestream(line);
		for (BYTE j = 0; j < aBoard[i].size(); ++j)
			linestream >> aCellValues[i][j];
	}

	for (BYTE i = 0; i < aCellValues.size(); ++i)
	{
		getline(aFileHandle, line);
		for (BYTE j = 0; j < aCellValues[i].size(); ++j)
			aBoard[i][j] = line[j];
	}
}

void Solve(string aInputFileName, string aOutputFileName)
{
	string mode;
	char youPlay;
	int maxDepth = 0;
	double timeLeft = 0;
	ifstream infile(aInputFileName);
	string line;
	getline(infile, line);
	stringstream ss(line);
	int tmp;
	ss >> tmp;
	BYTE dimension = static_cast<BYTE>(tmp);
	getline(infile, line);
	ss.str(line);
	ss.clear();
	ss >> mode;
	getline(infile, line);
	ss.str(line);
	ss.clear();
	ss >> youPlay;
	if (mode != "COMPETITION")
	{
		getline(infile, line);
		ss.str(line);
		ss.clear();
		ss >> tmp;
		maxDepth = static_cast<BYTE>(tmp);
	}
	else
	{
		getline(infile, line);
		ss.str(line);
		ss.clear();
		ss >> timeLeft;
	}
	vector<vector<char>> board(dimension, vector<char>(dimension, '.'));
	vector<vector<int>> cellValues(dimension, vector<int>(dimension, 0));
	LoadBoardFromFile(infile, board, cellValues);
	infile.close();
	tuple<string, string, string> result;	
	if (mode == "COMPETITION")
	{
		//AIPlayer aiPlayer(dimension, "ALPHABETA", youPlay, 2, timeLeft, board, cellValues);
		AIPlayerCompetitive aiPlayer(dimension, mode, youPlay, maxDepth, timeLeft, board, cellValues);
		result = aiPlayer.Solve();
	}
	else
	{
		AIPlayer aiPlayer(dimension, mode, youPlay, maxDepth, timeLeft, board, cellValues);
		result = aiPlayer.Solve();
	}
	ofstream outfile(aOutputFileName);
	outfile << get<0>(result) << ' ' << get<1>(result) << '\n' << get<2>(result);
	outfile.close();
}

int main()
{
	Solve("input.txt", "output.txt");
	return 0;
}