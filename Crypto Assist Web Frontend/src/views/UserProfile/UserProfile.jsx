import React, { Component } from 'react';
import {
    Grid, Row, Col,
    FormGroup, ControlLabel, FormControl
} from 'react-bootstrap';

import {Card} from 'components/Card/Card.jsx';
import {FormInputs} from 'components/FormInputs/FormInputs.jsx';
import {UserCard} from 'components/UserCard/UserCard.jsx';
import Button from 'elements/CustomButton/CustomButton.jsx';

import avatar from "assets/img/faces/face-3.jpg";

class UserProfile extends Component {
componentDidMount(){
    document.title = "Crypto Assist - User Profile";
}

    render() {
        return (
            <div className="content">
                <Grid fluid>
                    <Row>
                        <Col md={8}>
                            <Card
                                title="Edit Profile"
                                content={
                                    <form>
                                        <FormInputs
                                            ncols = {["col-md-6" , "col-md-6"]}
                                            proprieties = {[
                                                {
                                                 label : "API Key",
                                                 type : "text",
                                                 bsClass : "form-control",
                                                 placeholder : "API Key",
                                                 defaultValue : ""
                                                },
                                                {
                                                 label : "Secret",
                                                 type : "text",
                                                 bsClass : "form-control",
                                                 placeholder : "Secret",
                                                 defaultValue : ""
                                                }
                                            ]}
                                        />
                                        <Button
                                            bsStyle="info"
                                            pullRight
                                            fill
                                            type="submit"
                                        >
                                            Update
                                        </Button>
                                        <div className="clearfix"></div>
                                    </form>
                                }
                            />
                        </Col>


                    </Row>
                </Grid>
            </div>
        );
    }
}

export default UserProfile;
