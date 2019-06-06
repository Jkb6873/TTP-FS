import React from 'react';
import axios from 'axios';
import qs from 'qs';

class LoginForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      openTab: "login"
    };
  }

  selectTab(event, tabName) {
    this.setState({openTab: tabName});
  }

  render() {
    return (
      <div className="login-form-container">
        <div className="tabs">
          <div
            className="tab"
            onClick={this.selectTab.bind(this, 'login')}>
            Login
          </div>
          <div
            className="tab"
            onClick={this.selectTab.bind(this, 'register')}>
            Register
          </div>
        </div>

        <div className="tab-content">
          {this.state.openTab==="login"? <LogInTab/>: <CreateAccountTab/>}
        </div>

      </div>
    );

  }

}

class LogInTab extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      email: "",
      password: "",
      error: undefined
    };
  }

  handleChange(event) {
    this.setState({[event.target.name]: event.target.value})
  }

  logIn(event){
    this.setState({'error': undefined})
    axios.post("/login?" + qs.stringify({
      email: this.state.email,
      password: this.state.password
    })).catch((error) => this.setState({'error': error.response.data.error}))
  }

  render() {
    return (
      <div className="input-feild-container">
        <span className="error-text">{this.state.error? this.state.error: ''}</span>
        <div className="input-container">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            name="username"
            className="input-field"
            onChange={this.handleChange.bind(this)}
            placeholder="Username"/>
        </div>

        <div className="input-container">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            name="password"
            className="input-field"
            onChange={this.handleChange.bind(this)}
            placeholder="Password"/>
        </div>

        <button
          type="button"
          className="login-btn"
          onClick={this.logIn.bind(this)}>
          Login
        </button>
      </div>
    );
  }

}

class CreateAccountTab extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      name: "",
      email: "",
      password: "",
      error: undefined
    };
  }

  handleChange(event) {
    this.setState({[event.target.name]: event.target.value})
  }

  createAccount() {
    this.setState({'error': undefined})
    axios.post("/register?" + qs.stringify({
      name: this.state.name,
      email: this.state.email,
      password: this.state.password
    })).catch((error) => this.setState({'error': error.response.data.error}))
  }

  render() {
    return (
      <div className="input-feild-container">
        <span className="error-text">{this.state.error? this.state.error: ''}</span>
        <div className="input-container">
          <span htmlFor="name">Name</label>
          <input
            type="text"
            name="name"
            className="input-field"
            onChange={this.handleChange.bind(this)}
            placeholder="John Smith"/>
        </div>
        <div className="input-container">
          <label htmlFor="email">Email</label>
          <input
            type="text"
            name="email"
            className="input-field"
            onChange={this.handleChange.bind(this)}
            placeholder="jsmith@email.com"/>
        </div>
        <div className="input-container">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            name="password"
            className="input-field"
            onChange={this.handleChange.bind(this)}
            placeholder="*****"/>
        </div>
        <button
          type="button"
          className="login-button"
          onClick={this.createAccount.bind(this)}>
          Create An Account
        </button>

      </div>
    );
  }
}

export default LoginForm;
