import React from 'react';
import logo from './logo.svg';
import './App.css';
import LoginForm from './LoginForm';
import AccountForm from './AccountForm';

class App extends React.Component {

  //if there is no cookie present, show login page.
  //else if there is a cookie present, then the api will expire the cookie
  //and cause the person to log out.
  render(){
    var page = jwtExists ? <LoginForm/> : <AccountForm/>
    return (
      <LoginForm/>
    );
  }
}

function jwtExists(){
  var value = "; " + document.cookie;
  var parts = value.split("; " + 'site_token' + "=");
  if (parts.length == 2) return parts.pop().split(";").shift();
  else return undefined;
}




export default App
