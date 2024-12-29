# **Introduction to Apache Airflow**

## Objectives

- This guide will introduce you to Apache Airflow, it’s fundamentals and how it works.
- The creations of DAGs using various operators in Airflow will get familiar.
- Will help you to build connections between databases (Postgres) and Airflow.


## Table of Contents

- Introduction and Basic Concepts of Apache Airflow.
- Run Airflow 2.0 in docker container.
- Creating first DAG with BashOperator.
- Creating DAG with PythonOperator.
- Creating DAG with TaskFlow API.
- DAG with catchup and backfill.
- Scheduling with CRON expression.
- Airflow connection to connect Postgres.
- Use case of BranchPythonOperators.
- SubDAGs & TaskGroups.
- XComs.


## Basic Concepts of Apache Airflow

**Apache Airflow** is an open-source tool for orchestrating and automating workflows. It helps you define, schedule, and monitor workflows (tasks) programmatically using Python scripts. Workflows in Airflow are represented as Directed Acyclic Graphs (DAGs), which define the order and dependency of tasks.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/1.svg)


### Directed Acyclic Graph (DAG)  
A DAG is a workflow blueprint in Airflow that defines tasks and their dependencies. It ensures tasks execute in a directed (one-way) and acyclic (no loops) sequence, like extracting, processing, and loading data in order.

### Task  
A task is a single unit of work within a DAG, such as running code, executing SQL, or transferring files. Tasks are connected in a DAG to define execution order and dependencies.

### Operator  
An operator is a predefined template in Airflow that specifies what a task does, like running Python code (`PythonOperator`) or executing SQL queries (`PostgresOperator`). Tasks are created using operators.


![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/2.svg)


### Execution Date  
The execution date refers to the logical date and time a DAG run is associated with, not the actual runtime. It indicates when the DAG is scheduled to run, typically used to backfill or manage historical data workflows.



### Task Instance  
A task instance represents the specific execution of a task within a DAG run. It is a combination of a task, its DAG, and the execution date. Task instances track the status (e.g., running, failed, or success) of a task during a DAG run.



### DAG Run  
A DAG run is a specific instance of a DAG execution triggered by a schedule or manually. It groups all task instances for a given execution date, providing a snapshot of the DAG’s execution progress.



### Airflow Task Lifecycle  

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/7.svg)

1. **None**: The initial state before a task is scheduled.  
2. **Scheduled**: The task is queued for execution, waiting for available resources.  
3. **Queued**: The task is ready to run and waiting for a worker to pick it up.  
4. **Running**: The task is actively being executed by a worker.  
5. **Success**: The task has completed execution successfully.  
6. **Failed**: The task execution encountered an error and did not complete.  
7. **Retry**: The task is reattempting execution after a failure (if retries are configured).  
8. **Skipped**: The task was intentionally skipped, often due to upstream conditions or dependencies.  
9. **Up for Retry**: The task is awaiting its next retry attempt.  
10. **Upstream Failed**: The task did not execute because a dependency task failed.  
11. **Removed**: The task is removed from the DAG or disabled.  

This lifecycle ensures that tasks are tracked and managed effectively through their execution.


![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/6.svg)

This diagram provides a high-level overview of Apache Airflow's architecture. Here's a breakdown of its components:

1. **Data Engineer**:  
   Writes DAGs (workflows) using Python code and submits them to Airflow.

2. **DAGs**:  
   Represent workflows written by the engineer, stored in a specified directory.

3. **Metadata Database (Postgres)**:  
   Stores Airflow's metadata, including DAG definitions, task states, and scheduler status.

4. **Web Server**:  
   Hosts the Airflow UI, allowing users to view DAGs, monitor workflows, and manage executions.

5. **Scheduler**:  
   Determines when tasks should run based on the DAG definitions and triggers execution.

6. **Executor**:  
   Executes tasks either locally or distributed (e.g., Celery or Kubernetes Executors).

7. **Workers**:  
   Perform the actual execution of tasks as instructed by the executor.

8. **airflow.cfg**:  
   Configuration file for customizing Airflow's behavior, such as database connections and scheduling parameters.



## Run Airflow 2.0 in docker container

1. Installing docker community edition.
2. Creating a new folder named “Airflow docker” and open it in VSCode.
3. Checking if the docker community edition & the docker compose version working fine.

    ```bash
    docker --version
    docker-compose --version
    ```

4. Fetching the docker-compose.yaml file:

    ```bash
    curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.4/docker-compose.yaml'
    ```

5. The `docker-compose.yaml` file will show up on directory.

6. Editing the yaml file `AIRFLOW_CORE_EXECUTOR` from CeleryExecutor to LocalExecutor. Deleting not needed lines such:

    ```bash
    AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__BROKER_URL: redis://:@redis:6379/0
    ```

    redis, airflow-worker, flower.


    **ISSUE-01:** Was having problem regarding the edition of the yaml file. 

    Solution: 

    ```python
    docker-compose down
    ```

7. Copying the first line and run it on terminal. Second line is for linux user, as I am currently using mac, I don’t need to run it.

    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image2.webp)


8. Initializing the database:
    ```bash
    docker-compose up airflow-init
    ```

9. If you get this output, that means the airflow initialization is complete.

    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image3.webp)

10. Running the Airflow

    ```bash
    docker-compose up -d
    ```

11. To check what containers are running in the background:

    ```bash
    docker ps
    ```

## Launching using Poridhi Load Balancer


![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image4.webp)

1. Try getting the ip of your local machine using the command.
    
    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image5.webp)

2. Create Load Balancer and launch it.

    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image6.webp)
    


## Creating first DAG with BashOperator    

1. After logging in to the Apache Airflow using `<load-balancer-url>/home`, the dashboard is filled with example dags.

    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image7.webp)

2. To remove them following steps are needed to be taken:
    ```bash
    docker-compose down -v
    ```

    Change the AIRFLOW_CORE_LOAD_EXAMPLE from “true” to “false” in the yaml file.

    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image8.webp)

    Then reinitialize the database as did before. Will get output like this.

    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image9.webp)

3. Open a new file on “dag” folder.

    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image10.webp)


4. The code to create the first dag:

    ```py
    from datetime import datetime, timedelta
    from airflow import DAG
    from airflow.operators.bash import BashOperator


    default_args= {
        "owner": "nakib",
        "retries" : 5,
        "retry_delay": timedelta(minutes=2)
    }

    with DAG(
        dag_id= "Our_first_dag",
        default_args= default_args, 
        description="This is our first dag that we write",
        start_date= datetime(2024, 10, 12, 2),
        schedule="@daily"
    ) as dag:
        task1 = BashOperator(
            task_id= "first_task",
            bash_command="hello world, this is the first task"
        )
        task1
    ```

5. After a successful creation of DAG, it might look like this in the airflow dag dashboard.

    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image11.webp)


    The grid view

    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image12.webp)

6. Creating the second dag will be another easy task, using the same code with some changes.

    ```py
    from datetime import datetime, timedelta
    from airflow import DAG
    from airflow.operators.bash import BashOperator


    default_args= {
        "owner": "nakib",
        "retries" : 5,
        "retry_delay": timedelta(minutes=2)
    }

    with DAG(
        dag_id= "Our_first_dag_v2",
        default_args= default_args, 
        description="This is our first dag that we write",
        start_date= datetime(2024, 10, 12, 2),
        schedule="@daily"
    ) as dag:
        task1 = BashOperator(
            task_id= "first_task",
            bash_command="hello world, this is the first task"
        )
        task2 = BashOperator(
            task_id= "second_task",
            bash_command="I'm the second task and I'll be running after the first task"
        )
        task1.set_downstream(task2)
    ```

7. After running it, the airflow output will be seen like this

    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image13.webp)


8. In the grid view

    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image14.webp)
   


## Creating DAG using python operator

1. Code:

    ```py
    from datetime import datetime, timedelta
    from airflow import DAG
    from airflow.operators.python import PythonOperator

    default_args= {
        'owner': 'nakib',
        'retries': 5,
        'retry_delay': timedelta(minutes=5)
    }
    def greet(name, age):
        print(f"Hello world! My name is {name}, "
            f"I am {age} years old. ")

    with DAG(
        default_args=default_args,
        dag_id= 'First_dag_with_python_operator_v02',
        description= 'first dag creation with python operator',
        start_date= datetime(2024, 10, 12, 4),
        schedule= '@daily'
    ) as dag:
        task1 = PythonOperator(
            task_id= 'greet',
            python_callable= greet,
            op_kwargs= {'name ': 'Tom', 'age':20}
        )
        task1

2. After running the code and refreshing the DAG dashboard, our first dag with python operator is created!

    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image16.webp)

    When we want to share informations between tasks, we got to use XCom. Basically we can push information in one task and push that information in other task. Here is how to do it.


1. The function “greet” pulled the information that was pushed by the function “get_name”.

```py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args= {
    'owner': 'nakib',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}
def greet(ti, age):  #ti -> task instance
    name= ti.xcom_pull(task_ids='get_name')
    print(f"Hello world! My name is {name}, "
          f"I am {age} years old. ")

def get_name():
    return 'Jerry'

with DAG(
    default_args=default_args,
    dag_id= 'First_dag_with_python_operator_v03',
    description= 'first dag creation with python operator',
    start_date= datetime(2024, 10, 12, 4),
    schedule= '@daily'
) as dag:
    task1 = PythonOperator(
        task_id= 'greet',
        python_callable= greet,
        op_kwargs= {'age':20}
    )
    task2= PythonOperator(
        task_id= 'get_name',
        python_callable=get_name
    )
    task2 >> task1
```
​
2. DAG creation done.

    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image15.webp)

## Creating DAG with Taskflow API
Code:

```python
from datetime import datetime, timedelta

from airflow.decorators import dag, task

default_args= {
    'owner': 'nakib',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}


@dag(dag_id= "first_dag_with_taskflow_api",
     default_args=default_args,
     start_date=datetime(2024,10,12,6),
     schedule='@daily')

def hello_world_etl():

    @task()
    def get_name():
        return "Jerry"
    
    @task()
    def get_age():
        return 19
    
    @task()
    def greet(name, age):
        print(f"Hello world, My name is {name}, "
              f"and I am {age} years old")
        
    name= get_name()
    age= get_age()
    greet(name=name, age=age)

greet_dag = (hello_world_etl)
```


To get the multiple values out of a function, slight changes are needed.

1. Change the greet function.

```python
@task()
    def greet(first_name, last_name, age):
        print(f"Hello world, My name is {first_name} {last_name}, "
              f"and I am {age} years old")
```

2. Set multiple output parameter to true in the get_name function.

```python
@task(multiple_outputs=True)
    def get_name():
        return {
            'first_name' : 'Jerry',
            'last_name': 'fridmann'
        }
```

3. Get the name dictionary from get_name function and pass them to greet function.

```python
name_dict= get_name()
    age= get_age()
    greet(first_name= name_dict['first_name'],
          last_name= name_dict['last_name'],
          age=age)
```

4. Update the dag id version and run it.
5. It will create a new DAG.


## DAG with catchup and backfill

Both catchup and backfill are ways to run Airflow DAGs in the past. Here is an article to know the difference between both,
https://faun.pub/airflow-catchup-vs-backfill-22f3a7d4ba6f


```python
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args= {
    'owner': 'nakib',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id= 'dag_with_catchup_backfilll_v01',
    default_args=default_args,
    start_date= datetime(2024, 10, 1),
    schedule='@daily',
    catchup=True

) as dag:
    task1= BashOperator(
        task_id= 'task1',
        bash_command='Echo this is simple bash command'
    )
```    

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image17.webp)

The DAG has started since October 1st, 2024 and restarting once in everyday.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image18.webp)



```python
with DAG(
    dag_id= 'dag_with_catchup_backfilll_v02',
    default_args=default_args,
    start_date= datetime(2024, 10, 1),
    schedule='@daily',
    catchup=False
```

You can change the catchup to False to make it backfill, update the version and run it.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image19.webp)

You can still run the DAG using backfill. To know how follow the following steps,

1. Find the airflow scheduler container on VSCode using the command

```python
docker ps
```


2. Copy the scheduler id and run this command

```python
docker exec -it ff4bda0267bd /bin/bash
```

3. The output command terminal should be like this.

```python
airflow@ff4bda0267bd:/opt/airflow$
```

4. Run this command

```python
airflow dags backfill -s 2024-10-01 -e 2024-10-08
```

5. exit command to exit the container. Will see dag run from the starting date to end date.
    
    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image20.webp)
    

The code in dag dashboard.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image21.webp)


## ## Scheduling with Cron Expression

In Airflow, creating a DAG needs a schedule interval parameter. Which receives Cron Expression as String or datetime.timedelta as Object.

**What is a CRON Expression?**

A CRON expression is a string comprising five fields separated by white space that represents a set of times. Normally as a schedule to execute some routine.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image22.webp)

Airflow already provides some presets for CRON expression.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image23.webp)

But if you want to generate customised CRON expressions, you can make it in this website.

[https://crontab.guru](https://crontab.guru/)
















## Airflow connection to connect Postgres

- Go to the Admin > Connection > Add connection.
    
   ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image24.webp) 
    

- Change the yaml file, add port.
    
    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image25.webp)

- Download dbeaver and install it from here.

https://dbeaver.io/download/

- Start the airflow postgres container using the command.

```python
docker-compose up -d —no-deps —build postgres
```

- After completation the output would look like,
    
    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image26.webp)

- Open new file and run this code.

```python
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args= {
    "owner": "nakib",
    "retries" : 5,
    "retry_delay": timedelta(minutes=2)
}

with DAG(
    dag_id= "dag_with_postgres_operator_v02",
    default_args= default_args, 
    description="The first dag with postgres",
    start_date= datetime(2024, 10, 12),
    schedule= '0 0 * * *'
) as dag:
    task1 = PostgresOperator(
        task_id= 'create_postgres_table',
        postgres_conn_id='postgres_localhost',
        sql='''
            create table if not exist dag run (
                dt date,
                dag_id character varying,
                primary key (ds, dag_id)
                )'''
                
    )
    task1
```

- Save it and run it, it will show a new DAG in the dashboard.

    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image27.webp)

- The grid view
    
    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image28.webp)
    

- To insert informations to table add this bit of code and fix their task dependencies.

```python
task2 = PostgresOperator(
        task_id= 'insert_into_table',
        postgres_conn_id='postgres_localhost',
        sql="""
            insert into dag_runs (ds, dag_id) values ('{{ds}}','{{dag.dag_id}}')
        """
    )
    task1 >> task2
```

- In the same way you can delete content from table using this part of code.

```python
task3= PostgresOperator(
        task_id= 'delete_data_from_table',
        postgres_conn_id='postgres_localhost',
        sql="""
            delete from dag_runs where dt= '{{ds}}' and dag_id='{{dag.dag_id}}'
        """
    )
    task1 >> task3 >> task2
```

## Installation of python requirements via extending airflow docker image

- Open the docker project folder and open a new file “requirements.txt”.
    
    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image29.webp)

- Create a docker file in project root folder and give it as input

```docker
FROM apache/airflow:2.0.1
COPY requirements.txt /requirements.txt
RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user -r /requirements.txt
```

- In terminal run this command

```python
docker build . --tag extending_airflow:latest
```

Issue:

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image30.webp)


Solution:

Run this following commands:

```python
docker build --platform linux/amd64 . --tag extending_airflow:latest
```

- The code to execute the DAG

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'nakib',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

def get_sklearn():
    import sklearn
    print(f'scikit-learn with version: {sklearn.__version__}')

with DAG( 
    default_args=default_args,
    dag_id= 'dag_with_python_dependencies_v01',
    start_date= datetime(2024,10,8),
    schedule='@daily'
) as dag:
    
    get_sklearn= PythonOperator(
        task_id= 'get_sklearn',
        python_callable= get_sklearn
    )

    get_sklearn
```

## **BranchPythonOperator**

While scheduling tasks in airflow, sometimes there is a need of workflow to branch, or go through a certain path based on arbitrary condition. This is where the use of BranchPythonOperator comes for solution.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/5.svg)

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator
from datetime import datetime, timedelta

default_args={
    'start_date': datetime(2024,1,1)
}

def choose_best_model():
    accuracy=6
    if accuracy > 5:
        return 'accurate'
    elif accuracy <=5 :
        return 'inaccurate'

with DAG('branching', schedule_interval='@daily', default_args=default_args, catchup=False) as dag:
    
    choose_best_model= BranchPythonOperator(
        task_id= 'choose_best_model',
        python_callable=choose_best_model
    )

    accurate= BashOperator(
        task_id='accurate',
        bash_command='the model witll choose this if accuaracy is more than 5'
    )

    inaccurate= BashOperator(
        task_id='inaccurate',
        bash_command='model will choose this is accuracy is less than 5'
    )

    choose_best_model >> [accurate, inaccurate]
```

The code snippet defines a function where a condition of accuracy is given. If the condition satisfies, the accurate operator will succeed else the inaccurate operator.

Defining a function is a must thing to do here in branching. Otherwise it will send error for python_callable.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image31.webp)



If everything is done right it will show this as result:

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image32.webp)

### SubDags:

When adding exactly same set of tasks regularly to every DAG, or to group several tasks into a single logical unit, the use of SubDAGs arise.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image40.jpg)

The creation SubDAGs are divided into three phases.

1. Defining the subdag function.

```python
import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator

def subdag(parent_dag_name, child_dag_name, args):
    
    dag_subdag= DAG(
        dag_id=f'{parent_dag_name}.{child_dag_name}',
        default_args=args,
        start_date=pendulum.datetime(2024,1,1, tz='UTC'),
        catchup=False,
        schedule_interval='@daily',
    )

    for i in range(5):
        EmptyOperator(
            task_id= f'{child_dag_name}-task-{i+1}',
            default_args=args,
            dag=dag_subdag,
        )
        return dag_subdag
```

1. Parent DAG definition and putting the tasks in it with dependencies.

```python
from airflow import DAG
from airflow.example_dags.subdags.subdag import subdag
from airflow.operators.empty import EmptyOperator
from airflow.operators.subdag import SubDagOperator
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago

DAG_NAME= 'example_subdag_operator'

with DAG(
    dag_id=DAG_NAME,
    default_args={"retries":2},
    start_date=days_ago(2),
    schedule_interval="@once",
    tags=['example'],
) as dag:

    start= EmptyOperator(
        task_id='start'
    )

    section_1= SubDagOperator(
        task_id='section-1',
        subdag=subdag(DAG_NAME, 'section-1', dag.default_args),
    )

    some_other_task= EmptyOperator(
        task_id= 'some-other-task',
    )

    section_2= SubDagOperator(
        task_id= 'section-2',
        subdag=subdag(DAG_NAME, 'section-2', dag.default_args),
    )

    end= EmptyOperator(
        task_id='end',
    )

    start >> section_1 >> some_other_task >> section_2 >> end
```

The output shows parent DAGs which consists the child DAGs in it.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image33.webp)

### TaskGroups:

TaskGroups work similarly as SubDAGs, but with time TaskGroups has taken over SubDAGs with it’s efficiency and reliable behaviours.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image41.jpg)

We have divided the TaskGroup in few steps for better understanding of it.

Firstly, we tried to make the usual sequential code for Airflow scheduling.

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime , timedelta
from airflow.utils.task_group import TaskGroup

default_args= {
    'owner': 'local',
    'retries': 5,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='Taskgroups_dag',
    default_args=default_args,
    description='this is the tutorial dag for airflow taskgroups',
    start_date= datetime(2024,1,1),
    schedule='@daily',
)as dag:

    start= EmptyOperator(task_id='START')
    a= EmptyOperator(task_id='Task_A')
    a1= EmptyOperator(task_id='Task_A1')
    b= EmptyOperator(task_id='Task_B')
    c= EmptyOperator(task_id='Task_C')
    d= EmptyOperator(task_id='Task_D')
    e= EmptyOperator(task_id='Task_E')
    f= EmptyOperator(task_id='Task_F')
    g= EmptyOperator(task_id='Task_G')
    end= EmptyOperator(task_id='END')

start >> a >> a1 >> b >> c >> d >> e >> f >> g >> end
```

Which led us to get this output.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image34.webp)

Then, the Empty Operators (a, a1, b and c) are taken into a single group named gr_1. And we also have set the task dependencies for a and a1, where the other two tasks are independent.

```python
with TaskGroup("A-A1", tooltip="Task group for A and A1") as gr_1:
        a= EmptyOperator(task_id='Task_A')
        a1= EmptyOperator(task_id='Task_A1')
        b= EmptyOperator(task_id='Task_B')
        c= EmptyOperator(task_id='Task_C')
        a>>a1

start >> gr_1 >> d >> e >> f >> g >> end
```

The output will change to this:

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image35.webp)

And by clicking on the A-A1 task, we get the full view of the operations that’s happening within this.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image36.webp)

## XComs

XComs stands for cross communication and helps you to share messages and small amount of datas between tasks. An object where the value you want to exchange is stored inside the meta database of Airflow. So each time you are interacting with the XComs, you are interacting with the database of airflow. XComs mainly consists two arguments: Return_key which is the identity and Value, which holds the variable.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/3.svg)

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/4.svg)

For the purpose of learning, we can think of these DAGs where best of these three models will be chosen. When we process the values of three models and find an answer we push the value to XComs to send it to the next task.

To get the visual of the diagram, here’s the code snippet for that, where the models will choose any number between for their accuracy in between 0.1 to 10.

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from random import uniform
from datetime import datetime, timedelta

default_args= {
    'start_date': datetime(2024,1,1)
}

def training_model():
    accuracy= uniform(0.1, 10.0)
    print(f"model's accuracy: {accuracy}")
    return accuracy

def choose_best_model():
    print(f"choose best model")

with DAG(
    dag_id='x_coms_dag',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:
    downloading_data= BashOperator(
        task_id= 'downloading_data',
        bash_command='sleep 3'
    )

    training_model_task = [PythonOperator(
        task_id= f'training_model{task}',
        python_callable=training_model
    ) for task in ['A','B','C']]

    choose_model= PythonOperator(
        task_id= 'choose_model',
        python_callable=choose_best_model
    )

    downloading_data >> training_model_task >> choose_model
```

The DAGs will be created:

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image37.webp)

We can check the XComs from the Action tab.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image38.webp)

You can also push the XComs with your preferred return_key. To do that some slight changes like you need to access the task instance argument, which helps you to create a XCom with parameters key and value. 

```python
def training_model(task_instance):
    accuracy= uniform(0.1, 10.0)
    print(f"model's accuracy: {accuracy}")
    task_instance.xcom_push(key='model_accuracy', value=accuracy)
```

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Airflow%20Labs/Lab%2001/images/image39.webp)

**To call a XCom value in any function,**

```markup
task_instance.xcom_pull(key="identifier as string", task_ids="task-1")
```

## Conclusion

In this lab we completed the fundamentals of Apache Airflow including the theory and DAGs creation.
