import streamlit as st
import pandas as pd
import io
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from models.manage import get_questionnaire, get_open_ended_count_by_category, get_close_ended_count_by_category, add_question, update_question, delete_question, add_option, update_option, delete_option, log_import_start, log_import_completion

def show_manage_questions_page(): 
    st.title(" Manage Questionnaire")
    
    # Initialize session state for alerts
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False
    if 'form_message' not in st.session_state:
        st.session_state.form_message = ""
    if 'form_message_type' not in st.session_state:
        st.session_state.form_message_type = ""
    if 'edit_submitted' not in st.session_state:
        st.session_state.edit_submitted = False
    if 'edit_message' not in st.session_state:
        st.session_state.edit_message = ""
    if 'edit_message_type' not in st.session_state:
        st.session_state.edit_message_type = ""
    
    # Display success/error alerts at the top
    if st.session_state.form_message:
        if st.session_state.form_message_type == "success":
            st.markdown(f"""
            <div class="success-container">
                <h3 style="color: #059669;">✅ Success!</h3>
                <p style="color: #065f46;">{st.session_state.form_message}</p>
            </div>
            """, unsafe_allow_html=True)
        elif st.session_state.form_message_type == "error":
            st.markdown(f"""
            <div class="warning-container">
                <h3 style="color: #dc2626;">❌ Error!</h3>
                <p style="color: #7f1d1d;">{st.session_state.form_message}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Clear message after displaying
        st.session_state.form_message = ""
        st.session_state.form_message_type = ""
    
    if st.session_state.edit_message:
        if st.session_state.edit_message_type == "success":
            st.markdown(f"""
            <div class="success-container">
                <h3 style="color: #059669;">✅ Success!</h3>
                <p style="color: #065f46;">{st.session_state.edit_message}</p>
            </div>
            """, unsafe_allow_html=True)
        elif st.session_state.edit_message_type == "error":
            st.markdown(f"""
            <div class="warning-container">
                <h3 style="color: #dc2626;">❌ Error!</h3>
                <p style="color: #7f1d1d;">{st.session_state.edit_message}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Clear message after displaying
        st.session_state.edit_message = ""
        st.session_state.edit_message_type = ""
    
    # Add CSS for alert styling (same as questionnaire page)
    st.markdown("""
    <style>
    .warning-container {
        background-color: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 0.75rem;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    .success-container {
        background-color: #d1fae5;
        border: 1px solid #10b981;
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
    }
    .stForm button {
        background-color: var(--vibrant-blue);
        color: white;
    }
    .stForm button:hover {
        background-color: white;
        border: 2px solid var(--vibrant-blue);
    }
    [data-testid="stSliderThumbValue"] {
        color: var(--vibrant-blue);
        font-weight: bold;
    }
    .stSlider > div > div > div > div{
        background-color: var(--light-blue);
    }
    </style>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Existing Questions", "Add New Question", "Edit Questions", "Import Questions"])
    
    with tab1:
        questions = get_questionnaire()
        if not questions:
            st.info("No questions have been added yet.")
        else:
            # Group questions by category
            questions_by_category = {}
            for q in questions:
                category = q.get('Category', 'Uncategorized')
                if category not in questions_by_category:
                    questions_by_category[category] = []
                questions_by_category[category].append(q)
            
            # Display questions by category
            for category, category_questions in questions_by_category.items():
                st.subheader(f"Category: {category}")
                for q in category_questions:
                    with st.expander(f"{q['QuestionText']} ({q['QuestionType']}) - Weight: {q['Weight']}"):
                        if q['QuestionType'] == 'Close Ended' and q['Options']:
                            st.markdown("### Options:")
                            options_df = pd.DataFrame([
                                {"Option": opt['OptionText'], "Value": opt['OptionValue']} 
                                for opt in q['Options']
                            ])
                            options_df.index = range(1, len(options_df) + 1)
                            st.dataframe(options_df[["Option"]])
    
    def get_option_values(num_filled_options):
        """Generate option values based on the number of filled options"""
        if num_filled_options == 2:
            return [0.0, 1.0]
        elif num_filled_options == 3:
            return [0.0, 0.5, 1.0]
        elif num_filled_options == 4:
            return [0.0, 0.3, 0.6, 1.0]
        else:
            # Fallback for other cases (shouldn't happen with validation)
            return [round(i/(num_filled_options-1), 2) for i in range(num_filled_options)]
    
    with tab2:
        st.subheader("Add New Question")
        
        categories = get_question_categories()
        
        # Initialize form values in session state
        if 'form_question_text' not in st.session_state:
            st.session_state.form_question_text = ""
        if 'form_question_type' not in st.session_state:
            st.session_state.form_question_type = "Close Ended"
        if 'form_category' not in st.session_state:
            st.session_state.form_category = ""
        if 'form_weight' not in st.session_state:
            st.session_state.form_weight = 1
        if 'form_options' not in st.session_state:
            st.session_state.form_options = {}
        
        # Check if form was just submitted successfully to clear form
        if st.session_state.form_submitted and st.session_state.form_message_type == "success":
            clear_form_values()
            st.session_state.form_submitted = False
        
        question_type = st.selectbox("Question Type", 
                                       ["Close Ended", "Open Ended"], 
                                       index=0 if st.session_state.form_question_type == "Close Ended" else 1,
                                       key="input_question_type")
        
        with st.form("add_question_form", True):
            question_text = st.text_input("Question Text", 
                                        value=st.session_state.form_question_text, 
                                        key="input_question_text")
            
            # Category selection
            category_options = [""] + categories
            try:
                category_index = category_options.index(st.session_state.form_category)
            except ValueError:
                category_index = 0
            
            category = st.selectbox("Question Category", 
                                  category_options, 
                                  index=category_index,
                                  key="input_category")
            weight = st.slider("Question Weight/Importance", 
                             1, 10, 
                             st.session_state.form_weight,
                             key="input_weight")
            
            options = []
            if question_type == "Close Ended":
                st.markdown("### Add Options (Fill 2-4 options)")
                st.markdown("**Note:** You must fill at least 2 options and maximum 4 options. Empty options will be ignored.")
                
                # Always show 4 option fields
                option_texts = []
                for i in range(4):
                    option_text_key = f"opt_text_{i}"
                    option_text_value = st.session_state.form_options.get(f"text_{i}", "")
                    option_text = st.text_input(f"Option {i+1} (Optional for options 3-4)", 
                                              value=option_text_value, 
                                              key=option_text_key,
                                              placeholder=f"Enter option {i+1} text...")
                    option_texts.append(option_text.strip() if option_text else "")
                
                # Count filled options and create options list
                filled_options = [text for text in option_texts if text]
                num_filled = len(filled_options)
                
                if num_filled >= 2:
                    option_values = get_option_values(num_filled)
                    for i, text in enumerate(filled_options):
                        options.append({"text": text, "value": option_values[i]})
                    
            # Submit button with custom styling
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("Add Question", "Add new question to questionnaire", use_container_width=True)
            
            if submitted:
                st.session_state.form_submitted = True
                
                # Validation
                if not question_text.strip():
                    st.session_state.form_message = "Question text is required!"
                    st.session_state.form_message_type = "error"
                elif not category:
                    st.session_state.form_message = "Please select a question category!"
                    st.session_state.form_message_type = "error"
                elif question_type == "Close Ended":
                    # Check if category already has 2 Close Ended questions
                    existing_count = get_close_ended_count_by_category(category)
                    if existing_count >= 2:
                        st.session_state.form_message = f"Category '{category}' already has {existing_count} Close Ended questions. Maximum 2 Close Ended questions allowed per category!"
                        st.session_state.form_message_type = "error"
                    elif len(options) < 2:
                        st.session_state.form_message = "At least 2 options are required for closed-ended questions!"
                        st.session_state.form_message_type = "error"
                    elif len(options) > 4:
                        st.session_state.form_message = "Maximum 4 options are allowed for closed-ended questions!"
                        st.session_state.form_message_type = "error"
                    else:
                        # Proceed with adding question
                        success = add_question(question_text.strip(), question_type, category, weight, options)
                        
                        if success:
                            st.session_state.form_message = "Question added successfully! You can add another question or check the existing questions tab."
                            st.session_state.form_message_type = "success"
                        else:
                            st.session_state.form_message = "Failed to add question. Please try again."
                            st.session_state.form_message_type = "error"
                else:
                    # Check if category already has 1 Open Ended question
                    existing_open_count = get_open_ended_count_by_category(category)
                    if existing_open_count >= 1:
                        st.session_state.form_message = f"Category '{category}' already has {existing_open_count} Open Ended question. Maximum 1 Open Ended question allowed per category!"
                        st.session_state.form_message_type = "error"
                    else:
                        success = add_question(question_text.strip(), question_type, category, weight, None)
                        if success:
                            st.session_state.form_message = "Question added successfully! You can add another question or check the existing questions tab."
                            st.session_state.form_message_type = "success"
                        else:
                            st.session_state.form_message = "Failed to add question. Please try again."
                            st.session_state.form_message_type = "error"
                
                st.rerun()
    
    with tab4:
        show_import_section()
    
    with tab3:
        st.subheader("Edit or Delete Questions")
        
        questions = get_questionnaire()
        if not questions:
            st.info("No questions available to edit.")
            return
        
        # Select question to edit
        question_options = {q['QuestionID']: f"{q['QuestionText']} ({q['Category']})" for q in questions}
        selected_q_id = st.selectbox("Select Question to Edit", 
                                     options=list(question_options.keys()),
                                     format_func=lambda x: question_options[x])
        
        # Get the selected question
        selected_q = next((q for q in questions if q['QuestionID'] == selected_q_id), None)
        
        if selected_q:
            with st.form("edit_question_form"):
                st.markdown("### Edit Question")
                
                q_text = st.text_input("Question Text", value=selected_q['QuestionText'])
                q_category = st.selectbox("Category", get_question_categories(), 
                                          index=get_question_categories().index(selected_q['Category']) 
                                          if selected_q['Category'] in get_question_categories() else 0)
                q_weight = st.slider("Weight", 1, 10, int(selected_q['Weight']) if selected_q['Weight'] else 5)
                
                # If it's a close-ended question, show options
                if selected_q['QuestionType'] == 'Close Ended':
                    st.markdown("### Edit Options (2-4 options allowed)")
                    
                    # Get current options and pad to 4 slots
                    current_options = selected_q['Options'][:4]  # Limit to max 4
                    
                    # Create 4 input fields
                    option_texts = []
                    for i in range(4):
                        if i < len(current_options):
                            default_text = current_options[i]['OptionText']
                        else:
                            default_text = ""
                        
                        opt_text = st.text_input(f"Option {i+1} {'(Required)' if i < 2 else '(Optional)'}", 
                                               value=default_text, 
                                               key=f"edit_opt_text_{i}",
                                               placeholder=f"Enter option {i+1} text...")
                        option_texts.append(opt_text.strip() if opt_text else "")
                    
                    # Count filled options and show preview
                    filled_options = [text for text in option_texts if text]
                    num_filled = len(filled_options)
                    
                    if num_filled >= 2:
                        option_values = get_option_values(num_filled)
                        st.markdown("### Option Values Preview:")
                        preview_data = []
                        for i, text in enumerate(filled_options):
                            preview_data.append({"Option": text, "Value": option_values[i]})
                        preview_df = pd.DataFrame(preview_data)
                        preview_df.index = range(1, len(preview_df) + 1)
                        st.dataframe(preview_df[["Option"]])
                
                col1, col2 = st.columns(2)
                with col1:
                    update_button = st.form_submit_button("Update Question", type="primary", use_container_width=True)
                with col2:
                    delete_button = st.form_submit_button("Delete Question", type="secondary", use_container_width=True)
                
                if update_button:
                    st.session_state.edit_submitted = True
                    
                    # Validation
                    if not q_text.strip():
                        st.session_state.edit_message = "Question text cannot be empty!"
                        st.session_state.edit_message_type = "error"
                    elif selected_q['QuestionType'] == 'Close Ended':
                        filled_options = [text for text in option_texts if text]
                        if len(filled_options) < 2:
                            st.session_state.edit_message = "At least 2 options are required!"
                            st.session_state.edit_message_type = "error"
                        elif len(filled_options) > 4:
                            st.session_state.edit_message = "Maximum 4 options are allowed!"
                            st.session_state.edit_message_type = "error"
                        else:
                            # Update question
                            success = update_question(selected_q_id, q_text.strip(), q_category, q_weight)
                            
                            if success:
                                current_options = selected_q['Options']
                                option_values = get_option_values(len(filled_options))
                                options_success = True

                                for i, text in enumerate(filled_options):
                                    if i < len(current_options):
                                        opt_id = current_options[i]['OptionID']
                                        if not update_option(opt_id, text, option_values[i]):
                                            options_success = False
                                    else:
                                        if not add_option(selected_q_id, text, option_values[i], i + 1):
                                            options_success = False

                                # Delete extra old options
                                if len(current_options) > len(filled_options):
                                    for opt in current_options[len(filled_options):]:
                                        delete_option(opt['OptionID'])
                                
                                if options_success:
                                    st.session_state.edit_message = "Question and options updated successfully!"
                                    st.session_state.edit_message_type = "success"
                                else:
                                    st.session_state.edit_message = "Question updated, but there were some issues with options."
                                    st.session_state.edit_message_type = "error"
                            else:
                                st.session_state.edit_message = "Failed to update question. Please try again."
                                st.session_state.edit_message_type = "error"
                    else:
                        # For Open Ended questions
                        success = update_question(selected_q_id, q_text.strip(), q_category, q_weight)
                        if success:
                            st.session_state.edit_message = "Question updated successfully!"
                            st.session_state.edit_message_type = "success"
                        else:
                            st.session_state.edit_message = "Failed to update question. Please try again."
                            st.session_state.edit_message_type = "error"
                    
                    st.rerun()
                
                if delete_button:
                    st.session_state.edit_submitted = True
                    success = delete_question(selected_q_id)
                    
                    if success:
                        st.session_state.edit_message = "Question deleted successfully!"
                        st.session_state.edit_message_type = "success"
                    else:
                        st.session_state.edit_message = "Failed to delete question. Please try again."
                        st.session_state.edit_message_type = "error"
                    
                    st.rerun()
    
def clear_form_values():
    """Clear all form values in session state"""
    st.session_state.form_question_text = ""
    st.session_state.form_question_type = "Close Ended"
    st.session_state.form_category = ""
    st.session_state.form_weight = 5
    st.session_state.form_num_options = 4
    st.session_state.form_options = {}

def get_question_categories():
    return [
        'Social Interaction', 
        'Study Habits', 
        'Lifestyle', 
        'Cleanliness', 
        'Personal Values'
    ]
    
def show_import_section():
    st.subheader("Import Questions")
    st.markdown("Upload Excel file to update existing questions. Make sure to export first to get the correct format.")
    
    questions = get_questionnaire()
    if questions:
        export_data = []
        for q in questions:
            if q['QuestionType'] == 'Close Ended' and q.get('Options'):
                for opt in q['Options']:
                    export_data.append({
                        "QuestionID": q['QuestionID'],
                        "Category": q['Category'],
                        "QuestionText": q['QuestionText'],
                        "QuestionType": q['QuestionType'],
                        "Weight": q['Weight'],
                        "OptionID": opt.get('OptionID', ""),
                        "OptionText": opt['OptionText'],
                        "OptionValue": opt['OptionValue'],
                        "OptionOrder": opt.get('OptionOrder', "")
                    })
            else:
                export_data.append({
                    "QuestionID": q['QuestionID'],
                    "Category": q['Category'],
                    "QuestionText": q['QuestionText'],
                    "QuestionType": q['QuestionType'],
                    "Weight": q['Weight'],
                    "OptionID": "",
                    "OptionText": "",
                    "OptionValue": "",
                    "OptionOrder": ""
                })

        df_export = pd.DataFrame(export_data)

        wb = Workbook()
        ws = wb.active
        ws.title = "Questions Export"

        for r in dataframe_to_rows(df_export, index=False, header=True):
            ws.append(r)

        excel_buffer = io.BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)

        st.download_button(
            label=" Export Questions as Excel (Get Format)",
            data=excel_buffer,
            file_name="questionnaire_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download current questions to get the correct format for import",
            use_container_width=True
        )
        
        st.markdown("---")
    else:
        st.info("⚠️ No questions available to export. Add some questions first to get the import format.")
        st.markdown("---")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose Excel file", 
        type=['xlsx', 'xls'],
        help="Upload Excel file with question data to update"
    )
    
    if uploaded_file is not None:
        try:
            # Read Excel file
            df = pd.read_excel(uploaded_file)
                        
            # Validate data
            st.markdown("### Validation Results")
            with st.spinner("Validating data..."):
                validation_errors = validate_import_data(df)
            
            if validation_errors:
                st.error("❌ Validation failed!")
                for error in validation_errors:
                    st.error(f"• {error}")
                st.markdown("### Preview Data")
                st.dataframe(df)
                return
            else:
                st.success("✅ All data is valid!")
            

            # Show what will be updated
            questions_data = process_import_data(df)
            st.markdown("### Questions to be updated:")
            for q_id, q_data in questions_data.items():
                with st.expander(f"Question ID {q_id}: {q_data['QuestionText'][:50]}..."):
                    st.write(f"**Category:** {q_data['Category']}")
                    st.write(f"**Type:** {q_data['QuestionType']}")
                    st.write(f"**Weight:** {q_data['Weight']}")
                    if q_data['Options']:
                        st.write("**Options:**")
                        for opt in q_data['Options']:
                            st.write(f"  - {opt['OptionText']} (Value: {opt['OptionValue']})")
            
            # Confirm import
            if st.button("🚀 Import & Update Questions", type="primary"):
                with st.spinner("Updating questions..."):
                    success_count, error_messages = update_questions_from_import(questions_data)
                
                if error_messages:
                    st.warning(f"⚠️ {success_count} questions updated successfully, but some errors occurred:")
                    for error in error_messages:
                        st.error(f"• {error}")
                else:
                    st.success(f"🎉 Successfully updated {success_count} questions!")
                
                # Rerun to refresh the page
                st.rerun()
                
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.info("Please make sure the file is a valid Excel file with the correct format.")
            
def validate_import_data(df):
    errors = []
    
    required_headers = [
        'QuestionID', 'QuestionText', 'QuestionType', 'Category', 
        'Weight', 'OptionID', 'OptionText', 'OptionOrder', 'OptionValue'
    ]
    
    missing_headers = [header for header in required_headers if header not in df.columns]
    if missing_headers:
        errors.append(f"Missing required headers: {', '.join(missing_headers)}")
        return errors
    
    valid_types = ["Close Ended", "Open Ended"]
    valid_categories = [
        "Social Interaction", "Study Habits", "Lifestyle", 
        "Cleanliness", "Personal Values"
    ]
    
    category_type_counts = {}
    question_option_map = {}

    # Validate question rows
    unique_questions = df[['QuestionID', 'QuestionType', 'Category']].drop_duplicates()
    for _, row in unique_questions.iterrows():
        qtype = str(row['QuestionType']).strip()
        category = str(row['Category']).strip()

        key = (category, qtype)
        category_type_counts[key] = category_type_counts.get(key, 0) + 1
            
    for (category, qtype), count in category_type_counts.items():
        if qtype == "Close Ended" and count > 2:
            errors.append(f"Category '{category}' has {count} Close Ended questions. Maximum allowed is 2.")
        if qtype == "Open Ended" and count > 1:
            errors.append(f"Category '{category}' has {count} Open Ended questions. Maximum allowed is 1.")
    
    for qid, group in df.groupby('QuestionID'):
        qtype = str(group.iloc[0]['QuestionType']).strip()
        if qtype == "Close Ended":
            # Filter out blank option texts
            option_texts = group['OptionText'].dropna().apply(str).str.strip()
            option_values = group['OptionValue'].dropna().astype(float).tolist()

            filled_option_values = [v for i, v in enumerate(option_values) if option_texts.iloc[i] != '']
            filled_option_texts = [t for t in option_texts if t != '']

            num_options = len(filled_option_texts)
            expected_values = []

            if num_options == 2:
                expected_values = [0.0, 1.0]
            elif num_options == 3:
                expected_values = [0.0, 0.5, 1.0]
            elif num_options == 4:
                expected_values = [0.0, 0.3, 0.6, 1.0]
            else:
                errors.append(f"QuestionID {qid}: Must have 2 to 4 non-empty options. Found {num_options}.")
                continue

            if sorted(filled_option_values) != expected_values:
                errors.append(
                    f"QuestionID {qid}: OptionValues must be exactly {expected_values}. "
                    f"Found {sorted(filled_option_values)}."
                )
    
    for idx, row in df.iterrows():
        row_num = idx + 2  # +2 because DataFrame is 0-indexed and Excel rows start from 1, plus header row
        
        try:
            if pd.isna(row['QuestionID']) or row['QuestionID'] == '':
                errors.append(f"Row {row_num}: QuestionID cannot be empty")
            else:
                question_id = int(float(row['QuestionID']))  # float first to handle decimal, then int
                if question_id <= 0:
                    errors.append(f"Row {row_num}: QuestionID must be positive integer")
        except (ValueError, TypeError):
            errors.append(f"Row {row_num}: QuestionID must be integer")
        
        if pd.isna(row['QuestionText']) or str(row['QuestionText']).strip() == '':
            errors.append(f"Row {row_num}: QuestionText cannot be empty")
        elif len(str(row['QuestionText'])) > 255:
            errors.append(f"Row {row_num}: QuestionText exceeds 255 characters")
        
        if pd.isna(row['QuestionType']) or str(row['QuestionType']).strip() not in valid_types:
            errors.append(f"Row {row_num}: QuestionType must be exactly 'Close Ended' or 'Open Ended'")
        
        if pd.isna(row['Category']) or str(row['Category']).strip() not in valid_categories:
            errors.append(f"Row {row_num}: Category must be one of: {', '.join(valid_categories)}")
        
        try:
            if pd.isna(row['Weight']) or row['Weight'] == '':
                errors.append(f"Row {row_num}: Weight cannot be empty")
            else:
                weight = int(float(row['Weight']))
                if weight < 1 or weight > 10:
                    errors.append(f"Row {row_num}: Weight must be integer between 1-10")
        except (ValueError, TypeError):
            errors.append(f"Row {row_num}: Weight must be integer between 1-10")
        
        if not pd.isna(row['QuestionType']) and str(row['QuestionType']).strip() == "Close Ended":
            # Validasi OptionID
            if not pd.isna(row['OptionID']) and str(row['OptionID']).strip() != '':
                try:
                    option_id = int(float(row['OptionID']))
                    if option_id <= 0:
                        errors.append(f"Row {row_num}: OptionID must be positive integer")
                except (ValueError, TypeError):
                    errors.append(f"Row {row_num}: OptionID must be integer")
            
            if not pd.isna(row['OptionText']) and str(row['OptionText']).strip() != '':
                if len(str(row['OptionText'])) > 255:
                    errors.append(f"Row {row_num}: OptionText exceeds 255 characters")
            
            if not pd.isna(row['OptionOrder']) and str(row['OptionOrder']).strip() != '':
                try:
                    option_order = int(float(row['OptionOrder']))
                    if option_order <= 0:
                        errors.append(f"Row {row_num}: OptionOrder must be positive integer")
                except (ValueError, TypeError):
                    errors.append(f"Row {row_num}: OptionOrder must be integer")
            
            if not pd.isna(row['OptionValue']) and str(row['OptionValue']).strip() != '':
                try:
                    float(row['OptionValue'])
                except (ValueError, TypeError):
                    errors.append(f"Row {row_num}: OptionValue must be number")
    return errors

def process_import_data(df):
    # Group data by QuestionID
    questions_data = {}
    
    for idx, row in df.iterrows():
        q_id = int(float(row['QuestionID']))
        
        if q_id not in questions_data:
            questions_data[q_id] = {
                'QuestionID': q_id,
                'QuestionText': str(row['QuestionText']).strip(),
                'QuestionType': str(row['QuestionType']).strip(),
                'Category': str(row['Category']).strip(),
                'Weight': int(float(row['Weight'])),
                'Options': []
            }
        
        if (str(row['QuestionType']).strip() == "Close Ended" and 
            not pd.isna(row['OptionText']) and 
            str(row['OptionText']).strip() != ''):
            
            option_data = {
                'OptionID': int(float(row['OptionID'])) if not pd.isna(row['OptionID']) and str(row['OptionID']).strip() != '' else None,
                'OptionText': str(row['OptionText']).strip(),
                'OptionOrder': int(float(row['OptionOrder'])) if not pd.isna(row['OptionOrder']) and str(row['OptionOrder']).strip() != '' else len(questions_data[q_id]['Options']) + 1,
                'OptionValue': float(row['OptionValue']) if not pd.isna(row['OptionValue']) and str(row['OptionValue']).strip() != '' else 0.0
            }
            questions_data[q_id]['Options'].append(option_data)
    
    return questions_data

def update_questions_from_import(questions_data):
    success_count = 0
    error_messages = []
    
    # Log the import start
    import_job_id = log_import_start("Import Questions", len(questions_data))
    
    for q_id, q_data in questions_data.items():
        try:
            # Update question basic info
            success = update_question(
                q_id, 
                q_data['QuestionText'], 
                q_data['Category'], 
                q_data['Weight']
            )
            
            if success:
                if q_data['QuestionType'] == "Close Ended":
                    existing_question = next((q for q in get_questionnaire() if q['QuestionID'] == q_id), None)
                    
                    if existing_question and existing_question.get('Options'):
                        existing_option_ids = {opt['OptionID'] for opt in existing_question['Options']}
                        import_option_ids = {opt['OptionID'] for opt in q_data['Options'] if opt['OptionID']}
                        
                        for opt_id in existing_option_ids - import_option_ids:
                            delete_option(opt_id)
                        
                        for opt_data in q_data['Options']:
                            if opt_data['OptionID'] and opt_data['OptionID'] in existing_option_ids:
                                update_option(
                                    opt_data['OptionID'],
                                    opt_data['OptionText'],
                                    opt_data['OptionValue']
                                )
                            else:
                                add_option(
                                    q_id,
                                    opt_data['OptionText'],
                                    opt_data['OptionValue'],
                                    opt_data['OptionOrder']
                                )
                
                success_count += 1
            else:
                error_messages.append(f"Failed to update Question ID {q_id}")
                
        except Exception as e:
            error_messages.append(f"Error updating Question ID {q_id}: {str(e)}")
    
    # Log the import completion
    log_import_completion(import_job_id, success_count, len(error_messages))
    
    return success_count, error_messages