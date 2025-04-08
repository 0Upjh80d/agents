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
    return this.httpClient
      .post(`${this.baseUrl}/signup`, signup, {
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

  Orchestrator(userMessage: String): Observable<any> {
    const body = { message: userMessage };

    return this.httpClient.post(`${this.baseUrl}/dummy_orchestrator`, body).pipe(
      catchError(error => {
        return throwError(() => new Error(error.error?.detail ?? 'Error calling orchestrator'));
      })
    );
  }
}
