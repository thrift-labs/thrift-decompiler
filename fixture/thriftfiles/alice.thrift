include "bob.thrift"

namespace go alice_thrift
namespace py alice_thrift
namespace java alice_thrift

typedef i64 hello
typedef i32 int

struct AddParam {
    1: required i64 a;
    2: hello b = 1;
    3: optional string log;
}

service AliceService {
    int multiply(1:int n1, 2:int n2);
    i64 add(1: AddParam param);
}
