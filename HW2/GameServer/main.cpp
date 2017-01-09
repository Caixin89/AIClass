#include <vector>
#include <string>
#include <fstream>
#include <chrono>
#include <iostream>
#include <sstream>
#include <tuple>
#include <regex>

#define MAX_BOARD_DIMENSION 26
#define MIN_BOARD_DIMENSION 5
#define NUMBER_OF_ROUNDS 5
#define MAX_CELL_VAL 100
#define MIN_CELL_VAL 1
#define PLAYER_1_SYMBOL 'X'
#define PLAYER_2_SYMBOL 'O'
#define PLAYER_1_DIR "C:\\Users\\caixi\\Desktop\\Player1"
#define PLAYER_1_EXE_FILE "HW2.exe"
#define PLAYER_1_INPUT_FILE "input.txt"
#define PLAYER_1_OUTPUT_FILE "output.txt"
#define PLAYER_2_DIR "C:\\Users\\caixi\\Desktop\\Player2"
#define PLAYER_2_EXE_FILE "HW2.exe"
#define PLAYER_2_INPUT_FILE "input.txt"
#define PLAYER_2_OUTPUT_FILE "output.txt"

typedef unsigned char BYTE;

using namespace std;
using namespace chrono;

int player1Score = 0;
int player2Score = 0;
double timer1, timer2;
vector<vector<char>> board;
vector<vector<int>> cellValues;

void GenerateInputFile(string aFileName, char aPlayerSymbol, double aTimeLeft, vector<vector<char>> &aBoard, vector<vector<int>> &aCellValues) 
{
	ofstream fileStream(aFileName);
	fileStream << aBoard.size() << endl;
	fileStream << "COMPETITION" << endl;
	fileStream << aPlayerSymbol << endl;
	fileStream << aTimeLeft << endl;
	for (BYTE i = 0; i < aCellValues.size(); ++i)
	{
		for (BYTE j = 0; j < aCellValues.size(); ++j)
		{
			fileStream << aCellValues[i][j];
			if (j < aCellValues.size() - 1)
				fileStream << ' ';
		}
		fileStream << endl;
	}

	for (BYTE i = 0; i < aBoard.size(); ++i)
	{
		for (BYTE j = 0; j < aBoard.size(); ++j)
			fileStream << aBoard[i][j];
		fileStream << endl;
	}
	fileStream.close();
}

void InitRandomBoard(int aDimension)
{
	board.clear();
	for (BYTE i = 0; i < aDimension; ++i)
	{
		vector<char> boardRow;
		for (BYTE j = 0; j < aDimension; ++j)
		{
			int randNum = rand() % 3;			
			boardRow.push_back(randNum == 0 ? '.' : randNum == 1 ? 'X' : 'O');
		}
		board.push_back(boardRow);
	}
}

void InitBoard(int aDimension)
{
	board.clear();
	for (BYTE i = 0; i < aDimension; ++i)
	{
		vector<char> boardRow;
		for (BYTE j = 0; j < aDimension; ++j)
			boardRow.push_back('.');
		board.push_back(boardRow);
	}
}

void InitCellValues(int aDimension)
{
	cellValues.clear();
	for (BYTE i = 0; i < aDimension; ++i)
	{
		vector<int> cellValuesRow;
		for (BYTE j = 0; j < aDimension; ++j)
			cellValuesRow.push_back(rand() % (MAX_CELL_VAL - MIN_CELL_VAL + 1) + MIN_CELL_VAL);
		cellValues.push_back(cellValuesRow);
	}
}

bool IsGameOver()
{
	for (BYTE i = 0; i < board.size(); ++i)
		for (BYTE j = 0; j < board.size(); ++j)
			if (board[i][j] == '.')
				return false;
	return true;
}

int PlayerUtility(char aSymbol)
{
	int score = 0;
	for (BYTE i = 0; i < board.size(); ++i)
		for (BYTE j = 0; j < board.size(); ++j)
			if (board[i][j] == aSymbol)
				score += cellValues[i][j];
	return score;
}

void InitPlayer1()
{
	//make newgame
}

void InitPlayer2()
{
	//make newgame
}

void ExecutePlayer1()
{
	string cmd = "cd " + string(PLAYER_1_DIR) + "& .\\" + PLAYER_1_EXE_FILE;
	system(cmd.c_str());
}

void ExecutePlayer2()
{
	string cmd = "cd " + string(PLAYER_2_DIR) + "& .\\" + PLAYER_2_EXE_FILE;
	system(cmd.c_str());
}

void Init()
{
	timer1 = 200;
	timer2 = 200;
	srand(time(NULL));
	int dimension = rand() % (MAX_BOARD_DIMENSION - MIN_BOARD_DIMENSION + 1) + MIN_BOARD_DIMENSION;
	InitBoard(dimension);
	InitCellValues(dimension);
	InitPlayer1();
	InitPlayer2();
}

tuple<BYTE, BYTE> GetTilePosFromStr(string aStr)
{
	stringstream ss(aStr);
	char alphabet;
	int number;
	ss >> alphabet;
	ss >> number;
	return tuple<BYTE, BYTE>(alphabet - 'A', number - 1);
}

char GetOppositeSymbol(char aMySymbol)
{
	return aMySymbol == PLAYER_1_SYMBOL ? PLAYER_2_SYMBOL : PLAYER_1_SYMBOL;
}

bool EnterState(tuple<string, string> & aAction, char aMySymbol)
{
	string move, moveType;
	move = get<0>(aAction);
	moveType = get<1>(aAction);
	tuple<BYTE, BYTE> coord = GetTilePosFromStr(move);
	BYTE x = get<0>(coord);
	BYTE y = get<1>(coord);
	if (x < 0 || x >= board.size() || y < 0 || y >= board.size())
		return false;
	bool result = false;
	if (board[y][x] == '.')
	{
		if (moveType == "Stake")
		{
			board[y][x] = aMySymbol;
			result = true;
		}
		else if (moveType == "Raid")
		{
			board[y][x] = aMySymbol;
			char otherSymbol = GetOppositeSymbol(aMySymbol);
			if (x > 0 && board[y][x - 1] == otherSymbol)
			{
				board[y][x - 1] = aMySymbol;
			}
			if (x < board.size() - 1 && board[y][x + 1] == otherSymbol)
			{
				board[y][x + 1] = aMySymbol;
			}
			if (y > 0 && board[y - 1][x] == otherSymbol)
			{
				board[y - 1][x] = aMySymbol;
			}
			if (y < board.size() - 1 && board[y + 1][x] == otherSymbol)
			{
				board[y + 1][x] = aMySymbol;
			}
			result = true;
		}
	}
	return result;
}

void DisplayScore()
{
	cout << "GAME OVER!" << endl;
	if (player1Score > player2Score)
		cout << "PLAYER 1 WINS!!!" << endl;
	else if (player1Score == player2Score)
		cout << "DRAW!!!" << endl;
	else
		cout << "PLAYER 2 WINS!!" << endl;
	cout << "---SCORE---" << endl;
	cout << "PLAYER 1: " << player1Score << endl;
	cout << "PLAYER 2: " << player2Score << endl;
}

bool UpdateBoard(string aFileName, char aPlayerSymbol)
{
	ifstream fileStream(aFileName);
	string line;
	getline(fileStream, line);
	smatch match;
	regex reg("([A-Z][0-9]+) (Stake|Raid)");
	if (!regex_match(line, match, reg))
		return false;
	string move = match[1].str();
	string moveType = match[2].str();
	fileStream.close();
	//Change board based on move and moveType
	return EnterState(tuple<string, string>(move, moveType), aPlayerSymbol);
}

//---Player 1 (Goes first on odd turns)---
//Entry point: player1.exe
//Symbol: X

//---Player 2 (Goes first on even turns)---
//Entry point: player2.exe
//Symbol: O

int main()
{
	//initialise timer for both players
	for (int round = 1; round <= NUMBER_OF_ROUNDS; ++round)
	{
		//initialise
		Init();
		bool player1Turn = round % 2;
		while (true)
		{
			try
			{
				if (player1Turn) //Player 1 turn
				{
					GenerateInputFile(string(PLAYER_1_DIR) + "\\" + PLAYER_1_INPUT_FILE, PLAYER_1_SYMBOL, timer1, board, cellValues);
					high_resolution_clock::time_point startTime = high_resolution_clock::now();
					ExecutePlayer1();
					duration<double> time_span = duration_cast<duration<double>>(high_resolution_clock::now() - startTime);
					//---testing---//
					/*GenerateInputFile(string(PLAYER_2_DIR) + "\\" + PLAYER_2_INPUT_FILE, PLAYER_1_SYMBOL, timer1, board, cellValues);
					ExecutePlayer2();
					ifstream in1(string(PLAYER_1_DIR) + "\\" + PLAYER_1_OUTPUT_FILE);
					ifstream in2(string(PLAYER_2_DIR) + "\\" + PLAYER_2_OUTPUT_FILE);
					string line, line2;
					while (getline(in1, line) && getline(in2, line2))
					{
						if (line != line2)
						{
							cout << "Logic of Player1 is different from logic of Player2!" << endl;
							break;
						}
					}
					in1.close();
					in2.close();*/
					//------------//
					timer1 -= time_span.count();
					if (timer1 < 0)
					{
						//Time up, player 2 wins
						cout << "PLAYER 1 TIME UP, PLAYER 2 WINS ROUND " << round << '!' << endl;
						++player2Score;
						break;
					}
					if (!UpdateBoard(string(PLAYER_1_DIR) + "\\" + PLAYER_1_OUTPUT_FILE, PLAYER_1_SYMBOL))
					{
						//player 1 made an invalid move, player 2 wins
						cout << "PLAYER 1 MADE AN INVALID MOVE, PLAYER 2 WINS ROUND " << round << '!' << endl;
						++player2Score;
						break;
					}
					cout << "Player 1 score: " << PlayerUtility(PLAYER_1_SYMBOL) << endl;
					cout << "Player 1 time left: " << timer1 << endl;
				}
				else //Player 2 turn
				{
					GenerateInputFile(string(PLAYER_2_DIR) + "\\" + PLAYER_2_INPUT_FILE, PLAYER_2_SYMBOL, timer2, board, cellValues);
					high_resolution_clock::time_point startTime = high_resolution_clock::now();
					ExecutePlayer2();
					duration<double> time_span = duration_cast<duration<double>>(high_resolution_clock::now() - startTime);
					timer2 -= time_span.count();
					if (timer2 < 0)
					{
						//Time up, player 1 wins
						cout << "PLAYER 2 TIME UP, PLAYER 1 WINS ROUND " << round << '!' << endl;
						++player1Score;
						break;
					}
					if (!UpdateBoard(string(PLAYER_2_DIR) + "\\" + PLAYER_2_OUTPUT_FILE, PLAYER_2_SYMBOL))
					{
						//player 2 made an invalid move, player 1 wins
						cout << "PLAYER 2 MADE AN INVALID MOVE, PLAYER 1 WINS ROUND " << round << '!' << endl;
						++player1Score;
						break;
					}
					cout << "Player 2 score: " << PlayerUtility(PLAYER_2_SYMBOL) << endl;
					cout << "Player 2 time left: " << timer2 << endl;
				}
			}
			catch (exception)
			{
				if (player1Turn)
				{
					//player 2 gave corrupted output, player 1 wins
					cout << "PLAYER 2 GAVE A CORRUPTED OUTPUT, PLAYER 1 WINS ROUND " << round << '!' << endl;
					++player1Score;
				}
				else
				{
					//player 1 gave corrupted output, player 2 wins
					cout << "PLAYER 1 GAVE A CORRUPTED OUTPUT, PLAYER 2 WINS ROUND " << round << '!' << endl;
					++player2Score;
				}
				break;
			}
			//Check if game over
			if (IsGameOver())
			{
				int player1Utility = PlayerUtility(PLAYER_1_SYMBOL);
				int player2Utility = PlayerUtility(PLAYER_2_SYMBOL);
				if (player1Utility > player2Utility)
				{
					cout << "PLAYER 1 WINS ROUND " << round << '!' << endl;
					++player1Score;
				}
				else if (player2Utility > player1Utility)
				{
					cout << "PLAYER 2 WINS ROUND " << round << '!' << endl;
					++player2Score;
				}
				break;
			}
			player1Turn = !player1Turn;
		}
	}
	DisplayScore();
	cin.get();
	return 0;
}

