#include "mpi.h"
#include <cstdlib>
#include <cstdio>
#include <ctime>
#include <map>
#include <stack>
#include <Windows.h>
#include <vector>
#define REQUEST 0
#define RESPONSE 1


using std::stack;
using std::vector;

struct ForkMessage {
    int id;
    int sender;
    int type;
    ForkMessage(int _id, int _sender, int _type) : id(_id), sender(_sender), type(_type) {}
    ForkMessage() {}
};

struct Fork {
    int id;
    int owner;
    int alt_owner;
    bool clean;
    Fork(int _id, bool _clean, int _owner, int _alt_owner) :
        id(_id), clean(_clean), owner(_owner), alt_owner(_alt_owner) {}
};

void response(ForkMessage mess, vector<Fork>& forks, int j) {
    int i;
    for (i = 0; i < 2; i++)
        if (forks[i].id == mess.id) {
            forks[i].owner = j;
            forks[i].alt_owner = mess.sender;
            forks[i].clean = true;
        }
}

void request(ForkMessage mess, vector<Fork>& forks, stack<ForkMessage>& requests, int j) {
    int i;
    for (i = 0; i < 2; i++)
        if (forks[i].id == mess.id) {
            if (forks[i].owner == j) {
                if (forks[i].clean == true) {
                    requests.push(mess);
                }
                else {
                    ForkMessage outbound = ForkMessage(forks[i].id, j, RESPONSE);
                    forks[i].alt_owner = j;
                    forks[i].owner = mess.sender;
                    forks[i].clean = true;
                    MPI_Send(&outbound, sizeof(ForkMessage), MPI_BYTE, mess.sender, 0, MPI_COMM_WORLD);
                }
            }
            else { 
                requests.push(mess);
            }
        }
}

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    int  world_rank, world_size;
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);

    vector<Fork> forks;
    stack<ForkMessage> requests;

    if (world_rank != 0 && world_rank != world_size - 1) {
        forks.push_back(Fork(world_rank, false, world_rank - 1, world_rank));
        forks.push_back(Fork(world_rank + 1, false, world_rank, world_rank + 1));
    }
    if(world_rank == world_size-1) {
        forks.push_back(Fork(world_size - 1, false, world_size - 2, world_size - 1));
        forks.push_back(Fork(0, false, 0, world_size - 1));
    }
    if (world_rank == 0) {
        forks.push_back(Fork(0, false, 0, 1));
        forks.push_back(Fork(1, false, 0, 1));
    }

    srand(world_rank-5);
    while (true) {
        int flag,j=0;
        bool all_forks;
        printf("filozof %d misli\n", world_rank);
        fflush(stdout);

        while (j < rand() % 500) {
            j = j + 20;
            Sleep(600);
            MPI_Iprobe(MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, &flag, MPI_STATUS_IGNORE);
            if (flag) {
                ForkMessage receiving;
                MPI_Recv(&receiving, sizeof(ForkMessage), MPI_BYTE, MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                request(receiving, forks, requests, world_rank);
            }
        }

        do{
            all_forks = true;
            int i = 2;
            while (i-- > 0) {
                if (world_rank != forks[i].owner) {
                    printf("filozof %d trazi vilicu (%d)\n", world_rank, forks[i].id);
                    fflush(stdout);
                    ForkMessage mess = ForkMessage(forks[i].id, world_rank, REQUEST);
                    MPI_Send(&mess, sizeof(ForkMessage), MPI_BYTE, forks[i].owner, 0, MPI_COMM_WORLD);
                    all_forks = false;

                    while (forks[i].owner != world_rank) {
                        ForkMessage receiving;
                        MPI_Recv(&receiving, sizeof(ForkMessage), MPI_BYTE, MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                        if (receiving.type != RESPONSE)
                            request(receiving, forks, requests, world_rank);
                        else
                            response(receiving, forks, world_rank);
                    }
                }
            }

        } while (all_forks == false);
        printf("filozof %d jede\n", world_rank);
        fflush(stdout);

        forks[0].clean = false;
        forks[1].clean = false;

        while (requests.empty() == false) {
            ForkMessage top = requests.top(); 
            requests.pop();
            ForkMessage mess = ForkMessage(top.id, world_rank, REQUEST);
            MPI_Send(&mess, sizeof(ForkMessage), MPI_BYTE, top.sender, 0, MPI_COMM_WORLD);
        }
    }
    MPI_Finalize();
    return 0;
}
