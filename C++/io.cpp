#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <map>
using std::ifstream;
using std::ofstream;
using std::string;
using std::map;
using std::cout;
using std::endl;
using std::string;
using std::getline;
using std::runtime_error;
using std::istringstream;

map<string, string> buildMap(ifstream &map_file)
{
    map<string, string> trans_map;
    string key;
    string value;
    while (map_file >> key && getline(map_file, value)) {
        if (value.size() > 1)
            // trans_map[key] = value.substr(1); //跳过空格
            trans_map.insert({key, value.substr(1)});
        else
            throw runtime_error("no rule for " + key);
    }
    return trans_map;
}

const string &transform(const string &s, const map<string, string> &m)
{
    auto map_it = m.find(s);
    if (map_it != m.end()) {
        return map_it->second;
    } else {
        return s;
    }
}


void word_transform(ifstream &map_file, ifstream &input)
{
    auto trans_map = buildMap(map_file);
    string text;
    while (getline(input, text)) {
        istringstream stream(text);
        bool firstword = true;
        string word;
        while (stream >> word) {
            if (firstword)
                firstword = false;
            else
                cout << " ";
            cout << transform(word, trans_map);
        }
        cout << endl;
    }
    
}

int main()
{
    ifstream tran_map("map.txt");
    ifstream strs("test.txt");
    word_transform(tran_map, strs);
}

