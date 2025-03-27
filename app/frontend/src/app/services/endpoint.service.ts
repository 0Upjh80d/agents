import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Signup } from '../types/signup.type';
import { Login } from '../types/login.type';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class EndpointService {
  private baseUrl = 'http://localhost:8000';

  constructor(private httpClient: HttpClient) {}

  login(login: Login): Observable<any> {
    const formData = new HttpParams().set('username', login.username).set('password', login.password);

    return this.httpClient
      .post(`${this.baseUrl}/login`, formData.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      .pipe(
        catchError(error => {
          return throwError(() => new Error(error.error.detail));
        })
      );
  }

  signup(signup: Signup): Observable<any> {
    const data: Signup = {
      nric: signup.nric,
      first_name: signup.first_name,
      last_name: signup.last_name,
      email: signup.email,
      date_of_birth: signup.date_of_birth,
      gender: signup.gender,
      postal_code: signup.postal_code,
      password: signup.password,
      password_confirm: signup.password
    };

    return this.httpClient
      .post(`${this.baseUrl}/signup`, data, {
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .pipe(
        catchError(error => {
          return throwError(() => new Error(error.error.detail));
        })
      );
  }
}
