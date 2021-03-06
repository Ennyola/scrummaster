import { Injectable } from '@angular/core';
import { HttpClient,HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  public message;
  public goal_name;

  public login_username;
  public login_password;

  public createuser_username;
  public createuser_password;
  public createuser_rtpassword;
  public createuser_fullname;
  public createuser_age;
  public createuser_usertype;

  public username;
  public role;
  public users;

  public httpOptions = {
  headers: new HttpHeaders ({'content-Type' : 'application/json'})

  };

  public authOptions;

  constructor(private http: HttpClient, private router: Router) {
   }

  createUser()
  {
  	this.http.post('http://127.0.0.1:8000/medunoyeeniscrum/api/scrumusers/', JSON.stringify({'username' : this.createuser_username, 'password' : this.createuser_password,'rtpassword' : this.createuser_rtpassword, 'full_name' : this.createuser_fullname, 'age' : this.createuser_age, 'usertype' : this.createuser_usertype }),this.httpOptions).subscribe(

        data => {

          this.message = data['message']
          this.createuser_username = ''
          this.createuser_password = ''
          this.createuser_rtpassword = ''
          this.createuser_fullname = ''
          this.createuser_age = ''
          this.createuser_usertype = ''
        },
        err =>{
        this.message = 'User Creation Failed! Unexpected Error';
        console.error(err);
        this.createuser_username = ''
        this.createuser_password = ''
        this.createuser_rtpassword = ''
        this.createuser_fullname = ''
        this.createuser_age = ''
        this.createuser_usertype = ''

        }

    );
  }


  login(){

        this.http.post('http://127.0.0.1:8000/medunoyeeniscrum/api-token-auth/', JSON.stringify({'username' : this.login_username, 'password' : this.login_password }),this.httpOptions).subscribe(

        data => {
          sessionStorage.setItem('username', this.login_username);
          sessionStorage.setItem('role', data['role']);
          sessionStorage.setItem('token', data['token']);
          this.username = this.login_username;
          this.role = data['role'];
          this.message = 'Welcome';
          this.router.navigate(['profile']);
          this.login_username = '';
          this.login_password = '';
          console.log(data);

          this.authOptions = {

            headers: new HttpHeaders ({'content-Type' : 'application/json', 'Authorization' : 'JWT ' + data['token']})


          };

        },
        err =>{
        if(err['status'] == 400)
            this.message = 'Login Failed: Invalid Credentials.';
        else
            this.message = 'Login Failed! Unexpected Error';
        this.message = 'Login Failed! Unexpected Error';
        console.error(err);
         this.login_username = '';
         this.login_password = '';

        }
    );
  }

  addGoal()
  {

    this.http.post('http://127.0.0.1:8000/medunoyeeniscrum/api/scrumgoals/', JSON.stringify({'name': this.goal_name}),
    this.authOptions).subscribe(
        data => {
          this.users = data['data'];
          this.message = data['message'];
          this.goal_name = '';
        },
        err => {
            console.error(err);
             if(err['status'] == 401)
            {
                this.message = 'Session invalid or Expired. Please Login';
                this.logout();
            }else
            {
                this.message = 'Unexpected Error!'
            }
            this.goal_name = '';
        }
    );
  }



  logout(){

    this.username = '';
    this.role = '';
    this.users = [];
    this.router.navigate(['login']);
    this.authOptions = {};
    sessionStorage.removeItem('username');
    sessionStorage.removeItem('role');
    sessionStorage.removeItem('token');

  }

  moveGoal(goal_id , to_id)
  {

    this.http.patch('http://127.0.0.1:8000/medunoyeeniscrum/api/scrumgoals/', JSON.stringify({'goal_id' : goal_id , 'to_id' : to_id }),
    this.authOptions).subscribe(
        data => {
          this.users = data['data'];
          this.message = data['message'];
          
        },
        err => {
            console.error(err);

            if(err['status'] == 401)
            {
                this.message = 'Session invalid or Expired. Please Login.';
                this.logout();
            }else
            {
                this.message = 'Unexpected Error!'
            }
        }
    );


  }
  changeOwner(from_id,to_id){

     this.http.put('http://127.0.0.1:8000/medunoyeeniscrum/api/scrumgoals/', JSON.stringify({'mode': 0,'from_id' : from_id , 'to_id' : to_id }),
    this.authOptions).subscribe(
        data => {
          this.users = data['data'];
          this.message = data['message'];
          
        },
        err => {
             console.error(err);
             if(err['status'] == 401)
            {
                this.message = 'Session invalid or Expired. Please Login'
                this.logout();
            }else
            {
                this.message = 'Unexpected Error!'
            }
        }
    );

  }
}
 