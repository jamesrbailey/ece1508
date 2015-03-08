#include <boost/algorithm/string.hpp>
#include <iostream>
#include <sstream>
#include <map>
#include <vector>
#include <algorithm>

#define DEBUG_ON

#ifdef DEBUG_ON
#define DEBUG(x) do { std::cerr << x; } while (0)
#else
#define DEBUG(x)
#endif

using namespace std;

enum msg_val {NONE, E, ONE, ZERO};

class Variable;
class Check;

typedef map<Variable*, int> map_var_int;
typedef map<Variable*, int>::iterator map_var_int_it;

typedef map<Check*, int> map_chk_int;
typedef map<Check*, int>::iterator map_chk_int_it;

class Check {
public:
    int index;
    Check(int _index);
    map_var_int vars;
    int add_variable(Variable *v);
    void send_messages();
};

Check::Check(int _index) {
    index = _index;
    DEBUG("check " << index << " @" << this << " created" << endl);
}
void Check::send_messages() {
}


class Variable {
public:
    int index;
    Variable(int _index);
    map_chk_int chks;
    void send_messages();
    int get_value();

};


Variable::Variable(int _index) {
    index = _index;
    DEBUG("variable " << index << " @" << this << " created" << endl);
}
void Variable::send_messages() {
    //def send_messages(self):
    //    for check in self.checks: 
    //        message = self.init 
    //        for (c, u) in self.inbox.items():
    //            if c == check:
    //                continue
    //            elif u != -1:
    //                message = u
    //                break
    //            else:
    //                message = -1

    //        check.inbox[self] = message
}
int Variable::get_value() {
};

// TODO: only run BEC-SPA on undecoded variables
class Graph {
public:
    vector<Variable*> vars;
    vector<Check*> chks;

    Check* get_check(int index) {
        Check *c;
        int size = chks.size();
        if(index >= size) {
            chks.resize(index+1);
            for(int i = size; i <= index; i++) {
                chks[i] = new Check(i);
            }
        }
        c = chks[index];
        return c;
    }

    Variable* get_variable(int index) {
        Variable *v;
        int size = vars.size();
        if(index >= size) {
            vars.resize(index+1);
            for(int i = size; i <= index; i++) {
                vars[i] = new Variable(i);
            }
        }
        v = vars[index];
        return v;
    }

    int print_checks() {
        for(int i = 0; i < chks.size(); i++) {
            Check* c = chks[i];
            cout << "check " << i << ":";
            for(map_var_int_it it = c->vars.begin(); it != c->vars.end(); ++it) {
                cout << " " << it->first->index;
            }
            cout << endl;
        }
    }

    int print_variables() {
        for(int i = 0; i < vars.size(); i++) {
            Variable* v = vars[i];
            cout << "variable " << i << ":";
            for(map_chk_int_it it = v->chks.begin(); it != v->chks.end(); ++it) {
                cout << " " << it->first->index;
            }
            cout << endl;
        }
    }

    int connect(int c_idx, int v_idx) {
        DEBUG("connecting: " << c_idx << "," << v_idx << endl);
        Check *c = this->get_check(c_idx);
        Variable *v = this->get_variable(v_idx);
        c->vars[v] = NONE;
        //c->vars.insert(pair<Variable*,msg_val>(v, NONE));
        v->chks[c] = NONE;
    }
};


int main(int argc, char** argv) {

    Graph g;
    string line;
    int v_idx=0, c_idx=0;
    while (getline(cin, line))
    {
        istringstream iss(line);
        while (iss >> v_idx) {
            g.connect(c_idx, v_idx-1);
        } 
        c_idx++;
    }
    g.print_checks();
    g.print_variables();
}


        //cout << "check " << c << " variables:" << endl;
        //copy(int_vars.begin(), int_vars.end(), ostream_iterator<int>(cout, " "));
